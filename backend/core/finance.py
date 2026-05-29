from core.db import SessionLocal, Order, log_audit_event

def authorize_payment(order_id: int, amount: float, agent_name: str = "Finance Agent") -> bool:
    """
    Authorizes order payment. Rejects transactions over $500 to trigger a Saga rollback
    unless they have pre-approved waivers in the compliance logs.
    """
    # Exceeding $500 limit simulation to show Saga rollback
    if amount > 500.0:
        log_audit_event(
            agent_name=agent_name,
            action_type="PAYMENT_REJECTED",
            action_details=f"Order #{order_id} total ${amount:.2f} exceeds high-value compliance limits without waiver."
        )
        raise ValueError(f"Payment Authorization Denied: Order total ${amount:.2f} exceeds compliance limit of $500.00.")

    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        db.close()
        raise ValueError(f"Order #{order_id} not found.")

    order.status = "processing"
    db.commit()
    db.close()

    log_audit_event(
        agent_name=agent_name,
        action_type="PAYMENT_AUTHORIZED",
        action_details=f"Authorized ${amount:.2f} for Order #{order_id}."
    )
    return True

def void_payment(order_id: int, agent_name: str = "Finance Agent") -> bool:
    """
    Compensating action: Voids a previously authorized payment.
    """
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "pending"
        db.commit()
        
    db.close()
    log_audit_event(
        agent_name=agent_name,
        action_type="PAYMENT_VOIDED",
        action_details=f"Voided payment for Order #{order_id} due to downstream failure."
    )
    return True

def create_invoice(order_id: int, amount: float, agent_name: str = "Finance Agent") -> bool:
    """
    Generates a corporate invoice for the finalized order.
    """
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        db.close()
        raise ValueError(f"Order #{order_id} not found.")
        
    order.status = "invoiced"
    db.commit()
    db.close()

    log_audit_event(
        agent_name=agent_name,
        action_type="INVOICE_GENERATED",
        action_details=f"Generated invoice for Order #{order_id}."
    )
    return True

def cancel_invoice(order_id: int, agent_name: str = "Finance Agent") -> bool:
    """
    Compensating action: Cancels an invoice.
    """
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "cancelled"
        db.commit()
        
    db.close()
    log_audit_event(
        agent_name=agent_name,
        action_type="INVOICE_CANCELLED",
        action_details=f"Cancelled invoice for Order #{order_id} due to rollback."
    )
    return True
