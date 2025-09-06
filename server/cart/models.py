from pydantic import BaseModel, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        if v > 99:
            raise ValueError('Quantity cannot exceed 99')
        return v

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        if v > 99:
            raise ValueError('Quantity cannot exceed 99')
        return v

class CartItem(CartItemBase):
    id: int
    user_id: int
    product_name: str
    product_price: Decimal
    product_image: Optional[str] = None
    product_slug: str
    stock_quantity: int
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime

class CartDiscount(BaseModel):
    source: str  # e.g., 'promotion'
    code: Optional[str] = None
    description: Optional[str] = None
    amount: Decimal

class Cart(BaseModel):
    items: List[CartItem]
    total_items: int
    subtotal: Decimal
    # Promotions/discounts
    discount_total: Decimal = Decimal('0.00')
    applied_promo_code: Optional[str] = None
    # List of discount lines (e.g., promotions)
    # amount should be a positive decimal representing the discount magnitude
    discounts: List[CartDiscount] = []
    estimated_tax: Decimal
    estimated_shipping: Decimal
    estimated_total: Decimal

class CartSummary(BaseModel):
    item_count: int
    subtotal: Decimal
