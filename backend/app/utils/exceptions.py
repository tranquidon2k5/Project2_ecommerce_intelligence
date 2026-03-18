from fastapi import HTTPException, status


class ProductNotFoundException(HTTPException):
    def __init__(self, product_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PRODUCT_NOT_FOUND",
                "message": f"Product with id {product_id} not found"
            }
        )


class AlertNotFoundException(HTTPException):
    def __init__(self, alert_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ALERT_NOT_FOUND",
                "message": f"Alert with id {alert_id} not found"
            }
        )


class DatabaseException(HTTPException):
    def __init__(self, message: str = "Database error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DATABASE_ERROR",
                "message": message
            }
        )
