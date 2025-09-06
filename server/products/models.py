from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    name: str
    description: str
    price: Decimal
    category_id: int
    brand: str
    sku: str
    stock_quantity: int
    is_active: bool = True
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    tags: Optional[List[str]] = []
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class Product(ProductBase):
    id: int
    slug: str
    average_rating: Optional[float] = None
    review_count: int = 0
    image_urls: List[str] = []
    created_at: datetime
    updated_at: datetime

class ProductList(BaseModel):
    products: List[Product]
    total: int
    page: int
    per_page: int
    pages: int

class ProductFilters(BaseModel):
    category_id: Optional[int] = None
    brand: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    in_stock_only: bool = False
    tags: Optional[List[str]] = None
    search: Optional[str] = None

class ProductSort(BaseModel):
    field: str = "created_at"
    direction: str = "desc"
    
    @validator('field')
    def validate_sort_field(cls, v):
        allowed_fields = [
            'name', 'price', 'created_at', 'updated_at', 
            'average_rating', 'stock_quantity'
        ]
        if v not in allowed_fields:
            raise ValueError(f'Sort field must be one of: {", ".join(allowed_fields)}')
        return v
    
    @validator('direction')
    def validate_sort_direction(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort direction must be "asc" or "desc"')
        return v

class Category(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True
    sort_order: int = 0
    product_count: int = 0

class ProductImage(BaseModel):
    id: int
    product_id: int
    url: str
    alt_text: Optional[str] = None
    sort_order: int = 0
    is_primary: bool = False

class ProductReview(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    is_verified_purchase: bool = False
    created_at: datetime
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ProductReviewCreate(BaseModel):
    product_id: int
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v