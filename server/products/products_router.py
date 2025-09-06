from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from decimal import Decimal
import math

from products.models import (
    Product, ProductList, ProductFilters, ProductSort, 
    Category, ProductReview, ProductReviewCreate
)
from main import get_db, get_current_user, limiter

products_router = APIRouter()

@products_router.get("/", response_model=ProductList)
async def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    in_stock_only: bool = False,
    search: Optional[str] = None,
    sort_field: str = Query("created_at", alias="sort"),
    sort_direction: str = Query("desc", alias="order"),
    db=Depends(get_db)
):
    # Build WHERE clause
    where_conditions = ["p.is_active = true"]
    params = []
    param_count = 0
    
    if category_id:
        param_count += 1
        where_conditions.append(f"p.category_id = ${param_count}")
        params.append(category_id)
    
    if brand:
        param_count += 1
        where_conditions.append(f"LOWER(p.brand) = LOWER(${param_count})")
        params.append(brand)
    
    if min_price is not None:
        param_count += 1
        where_conditions.append(f"p.price >= ${param_count}")
        params.append(min_price)
    
    if max_price is not None:
        param_count += 1
        where_conditions.append(f"p.price <= ${param_count}")
        params.append(max_price)
    
    if in_stock_only:
        where_conditions.append("p.stock_quantity > 0")
    
    if search:
        param_count += 1
        where_conditions.append(f"""
            (LOWER(p.name) LIKE LOWER('%' || ${param_count} || '%') OR 
             LOWER(p.description) LIKE LOWER('%' || ${param_count} || '%') OR
             LOWER(p.brand) LIKE LOWER('%' || ${param_count} || '%'))
        """)
        params.append(search)
    
    where_clause = " AND ".join(where_conditions)
    
    # Validate sort parameters
    allowed_sort_fields = {
        'name': 'p.name',
        'price': 'p.price',
        'created_at': 'p.created_at',
        'updated_at': 'p.updated_at',
        'rating': 'p.average_rating',
        'stock': 'p.stock_quantity'
    }
    
    if sort_field not in allowed_sort_fields:
        sort_field = 'created_at'
    
    if sort_direction not in ['asc', 'desc']:
        sort_direction = 'desc'
    
    sort_clause = f"ORDER BY {allowed_sort_fields[sort_field]} {sort_direction.upper()}"
    
    # Get total count
    count_query = f"""
        SELECT COUNT(*) as total
        FROM products p
        WHERE {where_clause}
    """
    
    total_result = await db.fetchrow(count_query, *params)
    total = total_result['total']
    
    # Calculate pagination
    offset = (page - 1) * per_page
    pages = math.ceil(total / per_page)
    
    # Get products
    param_count += 1
    limit_param = param_count
    param_count += 1
    offset_param = param_count
    
    query = f"""
        SELECT 
            p.id, p.name, p.description, p.price, p.category_id, p.brand, 
            p.sku, p.slug, p.stock_quantity, p.is_active, p.weight, 
            p.dimensions, p.ingredients, p.instructions, p.tags, 
            p.average_rating, p.review_count, p.created_at, p.updated_at,
            COALESCE(
                ARRAY_AGG(pi.url ORDER BY pi.sort_order) FILTER (WHERE pi.url IS NOT NULL), 
                ARRAY[]::TEXT[]
            ) as image_urls
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE {where_clause}
        GROUP BY p.id, p.name, p.description, p.price, p.category_id, p.brand, 
                 p.sku, p.slug, p.stock_quantity, p.is_active, p.weight, 
                 p.dimensions, p.ingredients, p.instructions, p.tags, 
                 p.average_rating, p.review_count, p.created_at, p.updated_at
        {sort_clause}
        LIMIT ${limit_param} OFFSET ${offset_param}
    """
    
    params.extend([per_page, offset])
    products_data = await db.fetch(query, *params)
    
    products = []
    for row in products_data:
        product_dict = dict(row)
        product_dict['tags'] = product_dict['tags'] or []
        product_dict['image_urls'] = product_dict['image_urls'] or []
        products.append(Product(**product_dict))
    
    return ProductList(
        products=products,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )

@products_router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db=Depends(get_db)):
    query = """
        SELECT 
            p.id, p.name, p.description, p.price, p.category_id, p.brand, 
            p.sku, p.slug, p.stock_quantity, p.is_active, p.weight, 
            p.dimensions, p.ingredients, p.instructions, p.tags, 
            p.average_rating, p.review_count, p.created_at, p.updated_at,
            COALESCE(
                ARRAY_AGG(pi.url ORDER BY pi.sort_order) FILTER (WHERE pi.url IS NOT NULL), 
                ARRAY[]::TEXT[]
            ) as image_urls
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.id = $1 AND p.is_active = true
        GROUP BY p.id, p.name, p.description, p.price, p.category_id, p.brand, 
                 p.sku, p.slug, p.stock_quantity, p.is_active, p.weight, 
                 p.dimensions, p.ingredients, p.instructions, p.tags, 
                 p.average_rating, p.review_count, p.created_at, p.updated_at
    """
    
    product_data = await db.fetchrow(query, product_id)
    
    if not product_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product_dict = dict(product_data)
    product_dict['tags'] = product_dict['tags'] or []
    product_dict['image_urls'] = product_dict['image_urls'] or []
    
    return Product(**product_dict)

@products_router.get("/slug/{slug}", response_model=Product)
async def get_product_by_slug(slug: str, db=Depends(get_db)):
    query = """
        SELECT 
            p.id, p.name, p.description, p.price, p.category_id, p.brand, 
            p.sku, p.slug, p.stock_quantity, p.is_active, p.weight, 
            p.dimensions, p.ingredients, p.instructions, p.tags, 
            p.average_rating, p.review_count, p.created_at, p.updated_at,
            COALESCE(
                ARRAY_AGG(pi.url ORDER BY pi.sort_order) FILTER (WHERE pi.url IS NOT NULL), 
                ARRAY[]::TEXT[]
            ) as image_urls
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.slug = $1 AND p.is_active = true
        GROUP BY p.id, p.name, p.description, p.price, p.category_id, p.brand, 
                 p.sku, p.slug, p.stock_quantity, p.is_active, p.weight, 
                 p.dimensions, p.instructions, p.tags, 
                 p.average_rating, p.review_count, p.created_at, p.updated_at
    """
    
    product_data = await db.fetchrow(query, slug)
    
    if not product_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product_dict = dict(product_data)
    product_dict['tags'] = product_dict['tags'] or []
    product_dict['image_urls'] = product_dict['image_urls'] or []
    
    return Product(**product_dict)

@products_router.get("/categories/", response_model=List[Category])
async def get_categories(db=Depends(get_db)):
    query = """
        SELECT 
            c.id, c.name, c.slug, c.description, c.parent_id, 
            c.is_active, c.sort_order,
            COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id AND p.is_active = true
        WHERE c.is_active = true
        GROUP BY c.id, c.name, c.slug, c.description, c.parent_id, c.is_active, c.sort_order
        ORDER BY c.sort_order, c.name
    """
    
    categories_data = await db.fetch(query)
    return [Category(**dict(row)) for row in categories_data]

@products_router.get("/{product_id}/reviews", response_model=List[ProductReview])
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db=Depends(get_db)
):
    offset = (page - 1) * per_page
    
    query = """
        SELECT 
            pr.id, pr.product_id, pr.user_id, pr.rating, pr.title, 
            pr.comment, pr.is_verified_purchase, pr.created_at,
            u.first_name, u.last_name
        FROM product_reviews pr
        JOIN users u ON pr.user_id = u.id
        WHERE pr.product_id = $1
        ORDER BY pr.created_at DESC
        LIMIT $2 OFFSET $3
    """
    
    reviews_data = await db.fetch(query, product_id, per_page, offset)
    
    reviews = []
    for row in reviews_data:
        review_dict = dict(row)
        # Add user name for display
        review_dict['user_name'] = f"{row['first_name']} {row['last_name'][0]}."
        reviews.append(ProductReview(**review_dict))
    
    return reviews

@products_router.post("/{product_id}/reviews", response_model=ProductReview)
@limiter.limit("5/minute")
async def create_product_review(
    product_id: int,
    review_data: ProductReviewCreate,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    # Check if product exists
    product = await db.fetchrow(
        "SELECT id FROM products WHERE id = $1 AND is_active = true",
        product_id
    )
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user already reviewed this product
    existing_review = await db.fetchrow(
        "SELECT id FROM product_reviews WHERE product_id = $1 AND user_id = $2",
        product_id,
        user['id']
    )
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    # Check if user purchased this product (for verified purchase flag)
    purchase_query = """
        SELECT 1 FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE oi.product_id = $1 AND o.user_id = $2 AND o.status = 'delivered'
    """
    is_verified_purchase = bool(await db.fetchrow(purchase_query, product_id, user['id']))
    
    # Create review
    review = await db.fetchrow("""
        INSERT INTO product_reviews (
            product_id, user_id, rating, title, comment, 
            is_verified_purchase, created_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, product_id, user_id, rating, title, comment, 
                  is_verified_purchase, created_at
    """, 
        product_id, user['id'], review_data.rating, review_data.title,
        review_data.comment, is_verified_purchase, datetime.utcnow()
    )
    
    # Update product average rating and review count
    await db.execute("""
        UPDATE products SET 
            average_rating = (
                SELECT AVG(rating)::DECIMAL(3,2) 
                FROM product_reviews 
                WHERE product_id = $1
            ),
            review_count = (
                SELECT COUNT(*) 
                FROM product_reviews 
                WHERE product_id = $1
            )
        WHERE id = $1
    """, product_id)
    
    return ProductReview(**review)

@products_router.get("/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=20),
    db=Depends(get_db)
):
    query = """
        SELECT DISTINCT name, brand
        FROM products
        WHERE is_active = true 
        AND (LOWER(name) LIKE LOWER($1) OR LOWER(brand) LIKE LOWER($1))
        ORDER BY name
        LIMIT $2
    """
    
    search_term = f"%{q}%"
    suggestions = await db.fetch(query, search_term, limit)
    
    return {
        "suggestions": [
            {"text": row["name"], "type": "product"},
            {"text": row["brand"], "type": "brand"}
            for row in suggestions
        ]
    }