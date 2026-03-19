from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class CreateAlertRequest(BaseModel):
    product_id: int = Field(..., description="Product ID to monitor")
    user_email: EmailStr = Field(..., description="Email to send alert to")
    target_price: int = Field(..., gt=0, description="Target price in VND")
    alert_type: Literal["below", "above", "any_change"] = Field("below", description="Alert trigger type")


class AlertResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    user_email: str
    target_price: int
    alert_type: str
    is_triggered: bool
    triggered_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
