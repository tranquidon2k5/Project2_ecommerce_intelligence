import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.alert import PriceAlert
from ..models.product import Product

logger = logging.getLogger(__name__)


async def create_alert(
    db: AsyncSession,
    product_id: int,
    user_email: str,
    target_price: int,
    alert_type: str = "below",
) -> Optional[Dict]:
    """Create a new price alert."""

    # Verify product exists
    product_result = await db.execute(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    product = product_result.scalar_one_or_none()
    if not product:
        return None

    alert = PriceAlert(
        product_id=product_id,
        user_email=user_email,
        target_price=target_price,
        alert_type=alert_type,
        is_triggered=False,
        is_active=True,
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)

    return {
        "id": alert.id,
        "product_id": alert.product_id,
        "product_name": product.name,
        "user_email": alert.user_email,
        "target_price": alert.target_price,
        "alert_type": alert.alert_type,
        "is_triggered": alert.is_triggered,
        "triggered_at": alert.triggered_at,
        "is_active": alert.is_active,
        "created_at": alert.created_at,
    }


async def get_alerts_by_email(
    db: AsyncSession,
    user_email: str,
    page: int = 1,
    per_page: int = 20,
) -> tuple:
    """Get all alerts for a user."""

    query = (
        select(PriceAlert, Product.name.label("product_name"))
        .join(Product, PriceAlert.product_id == Product.id)
        .where(PriceAlert.user_email == user_email)
        .order_by(desc(PriceAlert.created_at))
    )

    from sqlalchemy import func
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    rows = result.all()

    alerts = [
        {
            "id": row[0].id,
            "product_id": row[0].product_id,
            "product_name": row[1],
            "user_email": row[0].user_email,
            "target_price": row[0].target_price,
            "alert_type": row[0].alert_type,
            "is_triggered": row[0].is_triggered,
            "triggered_at": row[0].triggered_at,
            "is_active": row[0].is_active,
            "created_at": row[0].created_at,
        }
        for row in rows
    ]

    return alerts, total


async def delete_alert(db: AsyncSession, alert_id: int) -> bool:
    """Delete an alert by ID."""

    result = await db.execute(select(PriceAlert).where(PriceAlert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        return False

    await db.delete(alert)
    return True


async def check_and_trigger_alerts(db: AsyncSession) -> int:
    """Check active alerts and trigger those where conditions are met."""

    triggered_count = 0

    # Get all active, untriggered alerts
    result = await db.execute(
        select(PriceAlert, Product.current_price.label("current_price"))
        .join(Product, PriceAlert.product_id == Product.id)
        .where(PriceAlert.is_active == True, PriceAlert.is_triggered == False)
    )
    rows = result.all()

    for row in rows:
        alert, current_price = row[0], row[1]

        should_trigger = False

        if alert.alert_type == "below" and current_price <= alert.target_price:
            should_trigger = True
        elif alert.alert_type == "above" and current_price >= alert.target_price:
            should_trigger = True
        elif alert.alert_type == "any_change":
            should_trigger = True

        if should_trigger:
            alert.is_triggered = True
            alert.triggered_at = datetime.utcnow()
            triggered_count += 1
            logger.info(f"Alert {alert.id} triggered for {alert.user_email}: product {alert.product_id} at {current_price}")

    return triggered_count
