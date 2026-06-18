from typing import Dict, Any, List
from core.db import SessionLocal, Order, OrderItem, Product, log_audit_event
from core.inventory import deduct_stock, restore_stock
from core.finance import authorize_payment, void_payment, create_invoice, cancel_invoice

class ProcureToPaySaga:
    def __init__(self, product_id: int, quantity: int, price: float, user_id: int = 3, agent_name: str = "Procure-to-Pay Agent"):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.user_id = user_id
        self.amount = round(quantity * price, 2)
        self.agent_name = agent_name
        self.order_id = None
        
        # Saga transaction states
        self.state = {
            "order_id": None,
            "stock_deducted": False,
            "payment_authorized": False,
            "invoice_generated": False,
            "logs": [],
            "status": "pending",
            "error": ""
        }

    def run(self) -> Dict[str, Any]:
        self.state["logs"].append("Initiating Procure-to-Pay Saga distributed workflow.")
        
        # Step 0: Create draft order
        db = SessionLocal()
        try:
            draft_order = Order(
                user_id=self.user_id,
                total_amount=self.amount,
                status="pending"
            )
            db.add(draft_order)
            db.commit()
            self.order_id = draft_order.id
            self.state["order_id"] = self.order_id
            
            # Create order item link
            item = OrderItem(
                order_id=self.order_id,
                product_id=self.product_id,
                quantity=self.quantity,
                unit_price=self.price
            )
            db.add(item)
            db.commit()
            self.state["logs"].append(f"Transaction #0: Draft Order #{self.order_id} generated.")
        except Exception as e:
            db.close()
            self.state["error"] = f"Failed to generate draft order: {str(e)}"
            self.state["status"] = "failed"
            return self.state
        finally:
            db.close()

        # Step 1: Deduct Stock
        try:
            self.state["logs"].append("Transaction #1: Attempting to deduct stock from inventory...")
            deduct_stock(self.product_id, self.quantity, agent_name=self.agent_name)
            self.state["stock_deducted"] = True
            self.state["logs"].append(f"Transaction #1 Success: Stock allocation complete (-{self.quantity} units).")
        except Exception as e:
            self.state["logs"].append(f"Transaction #1 Failure: {str(e)}")
            self.state["error"] = str(e)
            self._rollback()
            return self.state

        # Step 2: Authorize Payment
        try:
            self.state["logs"].append("Transaction #2: Attempting payment authorization...")
            authorize_payment(self.order_id, self.amount, agent_name=self.agent_name)
            self.state["payment_authorized"] = True
            self.state["logs"].append(f"Transaction #2 Success: Authorized payment of ${self.amount:.2f}.")
        except Exception as e:
            self.state["logs"].append(f"Transaction #2 Failure: {str(e)}")
            self.state["error"] = str(e)
            self._rollback()
            return self.state

        # Step 3: Create Invoice
        try:
            self.state["logs"].append("Transaction #3: Attempting invoice generation...")
            create_invoice(self.order_id, self.amount, agent_name=self.agent_name)
            self.state["invoice_generated"] = True
            self.state["logs"].append(f"Transaction #3 Success: Final invoice created successfully.")
            self.state["status"] = "completed"
        except Exception as e:
            self.state["logs"].append(f"Transaction #3 Failure: {str(e)}")
            self.state["error"] = str(e)
            self._rollback()
            return self.state

        return self.state

    def _rollback(self):
        self.state["status"] = "compensating"
        self.state["logs"].append("Saga transaction aborted. Launching backward compensating logic sequence (compensation):")
        
        # Compensate Invoice
        if self.state["invoice_generated"]:
            try:
                self.state["logs"].append("Compensator #3: Cancelling generated invoice...")
                cancel_invoice(self.order_id, agent_name=self.agent_name)
                self.state["invoice_generated"] = False
                self.state["logs"].append("Compensator #3 Success: Invoice cancelled.")
            except Exception as e:
                self.state["logs"].append(f"Compensator #3 Error: {str(e)}")
                
        # Compensate Payment
        if self.state["payment_authorized"]:
            try:
                self.state["logs"].append("Compensator #2: Voiding payment authorization...")
                void_payment(self.order_id, agent_name=self.agent_name)
                self.state["payment_authorized"] = False
                self.state["logs"].append("Compensator #2 Success: Payment voided.")
            except Exception as e:
                self.state["logs"].append(f"Compensator #2 Error: {str(e)}")

        # Compensate Stock
        if self.state["stock_deducted"]:
            try:
                self.state["logs"].append("Compensator #1: Restoring inventory stock allocations...")
                restore_stock(self.product_id, self.quantity, agent_name=self.agent_name)
                self.state["stock_deducted"] = False
                self.state["logs"].append(f"Compensator #1 Success: Stock allocation restored (+{self.quantity} units).")
            except Exception as e:
                self.state["logs"].append(f"Compensator #1 Error: {str(e)}")

        # Finally update Order status to cancelled
        db = SessionLocal()
        order = db.query(Order).filter(Order.id == self.order_id).first()
        if order:
            order.status = "cancelled"
            db.commit()
        db.close()
        
        self.state["logs"].append("Compensating sequence finalized. Database integrity restored.")
        self.state["status"] = "compensated"
