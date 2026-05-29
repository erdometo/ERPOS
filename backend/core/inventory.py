from core.db import SessionLocal, Product, log_audit_event

def deduct_stock(product_id: int, quantity: int, agent_name: str = "Inventory Agent") -> bool:
    """
    Deducts product stock for a purchase order.
    Throws ValueError if stock is insufficient.
    """
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        db.close()
        raise ValueError(f"Product #{product_id} not found.")

    if product.stock_quantity < quantity:
        db.close()
        raise ValueError(f"Insufficient stock for Product '{product.name}' (Available: {product.stock_quantity}, Requested: {quantity}).")

    product.stock_quantity -= quantity
    db.commit()
    db.close()

    log_audit_event(
        agent_name=agent_name,
        action_type="INVENTORY_ALLOCATED",
        action_details=f"Deducted {quantity} units from Product ID {product_id}."
    )
    return True

def restore_stock(product_id: int, quantity: int, agent_name: str = "Inventory Agent") -> bool:
    """
    Compensating action: Restores stock balance.
    """
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.stock_quantity += quantity
        db.commit()
        
    db.close()
    log_audit_event(
        agent_name=agent_name,
        action_type="INVENTORY_RESTORED",
        action_details=f"Restored {quantity} units to Product ID {product_id} due to transactional rollback."
    )
    return True
