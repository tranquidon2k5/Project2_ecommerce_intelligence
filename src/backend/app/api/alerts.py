from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.alert_service import (
    create_alert, get_alerts_by_email, delete_alert
)
from ..utils.exceptions import AlertNotFoundException

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def success_response(data, meta=None):
    return {"success": True, "data": data, "meta": meta, "message": None}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_price_alert(
    product_id: int,
    user_email: str,
    target_price: int,
    alert_type: str = "below",
    db: AsyncSession = Depends(get_db),
):
    """Create a new price alert."""
    alert = await create_alert(
        db,
        product_id=product_id,
        user_email=user_email,
        target_price=target_price,
        alert_type=alert_type,
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PRODUCT_NOT_FOUND", "message": f"Product {product_id} not found"}
        )

    return success_response(alert)


@router.post("/create")
async def create_price_alert_json(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """Create a new price alert (JSON body)."""
    alert = await create_alert(
        db,
        product_id=request["product_id"],
        user_email=request["user_email"],
        target_price=request["target_price"],
        alert_type=request.get("alert_type", "below"),
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PRODUCT_NOT_FOUND", "message": f"Product not found"}
        )

    return success_response(alert)


@router.get("")
async def list_alerts(
    email: str = Query(..., description="User email"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get all alerts for a user email."""
    alerts, total = await get_alerts_by_email(db, email, page=page, per_page=per_page)

    total_pages = (total + per_page - 1) // per_page
    meta = {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages}
    return success_response(alerts, meta)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an alert."""
    deleted = await delete_alert(db, alert_id)
    if not deleted:
        raise AlertNotFoundException(alert_id)
