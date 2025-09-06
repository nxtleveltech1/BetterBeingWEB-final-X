from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any

from cart.models import Cart, CartItem, CartItemCreate, CartItemUpdate, CartSummary, CartDiscount
from main import get_db, get_current_user, limiter, get_redis

cart_router = APIRouter()

def calculate_estimated_tax(subtotal: Decimal) -> Decimal:
    """Calculate estimated tax (15% VAT for South Africa)"""
    return subtotal * Decimal('0.15')

def calculate_estimated_shipping(subtotal: Decimal) -> Decimal:
    """Calculate estimated shipping costs"""
    if subtotal >= Decimal('500.00'):  # Free shipping over R500
        return Decimal('0.00')
    return Decimal('75.00')  # Standard shipping fee

async def _compute_discount_for_code(db, user_id: int, subtotal: Decimal, estimated_shipping: Decimal, code: Optional[str]) -> Dict[str, Any]:
    """Validate and compute discount for a given code based on current cart."""
    if not code:
        return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": None}

    # Fetch discount code
    discount = await db.fetchrow(
        """
        SELECT id, code, name, type, value, minimum_order_amount, maximum_discount_amount,
               usage_limit, usage_limit_per_customer, used_count, applies_to,
               applicable_product_ids, applicable_category_ids,
               starts_at, ends_at, is_active
        FROM discount_codes
        WHERE LOWER(code) = LOWER($1)
        """,
        code
    )

    if not discount:
        return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": None}

    # Validate basic flags
    from datetime import datetime as _dt
    now = _dt.utcnow()
    if not discount["is_active"]:
        return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": None}
    if discount["starts_at"] and now < discount["starts_at"]:
        return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": None}
    if discount["ends_at"] and now > discount["ends_at"]:
        return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": None}
    if discount["usage_limit"] is not None and discount["used_count"] >= discount["usage_limit"]:
        return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": None}

    # Per-customer limit (based on prior orders usage)
    if discount["usage_limit_per_customer"] is not None and discount["usage_limit_per_customer"] > 0:
        used_by_customer = await db.fetchval(
            "SELECT COUNT(*) FROM discount_code_uses WHERE discount_code_id = $1 AND user_id = $2",
            discount["id"], user_id
        )
        if used_by_customer and used_by_customer >= discount["usage_limit_per_customer"]:
            return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": None}

    # Min order value
    if discount["minimum_order_amount"] is not None and subtotal < discount["minimum_order_amount"]:
        return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": code}

    # Compute eligible subtotal based on applies_to
    applies_to = (discount["applies_to"] or 'all').lower()
    eligible_subtotal = subtotal
    if applies_to == 'specific_products' and discount["applicable_product_ids"]:
        eligible_subtotal = await db.fetchval(
            """
            SELECT COALESCE(SUM(ci.quantity * p.price), 0)
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = $1 AND p.is_active = true AND ci.product_id = ANY($2)
            """,
            user_id, discount["applicable_product_ids"]
        ) or Decimal('0.00')
    elif applies_to == 'specific_categories' and discount["applicable_category_ids"]:
        eligible_subtotal = await db.fetchval(
            """
            SELECT COALESCE(SUM(ci.quantity * p.price), 0)
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = $1 AND p.is_active = true AND p.category_id = ANY($2)
            """,
            user_id, discount["applicable_category_ids"]
        ) or Decimal('0.00')

    discount_amount = Decimal('0.00')
    description = discount["name"] or "Promotion"
    dtype = (discount["type"] or '').lower()

    if dtype == 'percentage':
        discount_amount = (eligible_subtotal * (Decimal(discount["value"]) / Decimal('100'))).quantize(Decimal('0.01'))
    elif dtype == 'fixed_amount':
        discount_amount = min(Decimal(discount["value"]), eligible_subtotal)
    elif dtype == 'free_shipping':
        discount_amount = (Decimal(estimated_shipping) if estimated_shipping else Decimal('0.00')).quantize(Decimal('0.01'))

    # Cap by maximum_discount_amount
    if discount["maximum_discount_amount"] is not None:
        discount_amount = min(discount_amount, Decimal(discount["maximum_discount_amount"]))

    if discount_amount <= 0:
        return {"discount_total": Decimal('0.00'), "discounts": [], "applied_code": code}

    return {
        "discount_total": discount_amount,
        "discounts": [
            {
                "source": "promotion",
                "code": discount["code"],
                "description": description,
                "amount": discount_amount,
            }
        ],
        "applied_code": discount["code"],
    }


async def build_cart_response(user, db, redis) -> Cart:
    query = """
        SELECT 
            ci.id, ci.user_id, ci.product_id, ci.quantity, ci.created_at, ci.updated_at,
            p.name as product_name, p.price as product_price, p.slug as product_slug,
            p.stock_quantity, pi.url as product_image,
            (ci.quantity * p.price) as subtotal
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        LEFT JOIN product_images pi ON p.id = pi.product_id AND pi.is_primary = true
        WHERE ci.user_id = $1 AND p.is_active = true
        ORDER BY ci.created_at DESC
    """

    cart_items_data = await db.fetch(query, user['id'])

    cart_items: List[CartItem] = []
    subtotal = Decimal('0.00')

    for row in cart_items_data:
        item_dict = dict(row)
        cart_items.append(CartItem(**item_dict))
        subtotal += item_dict['subtotal']

    estimated_tax = calculate_estimated_tax(subtotal)
    estimated_shipping = calculate_estimated_shipping(subtotal)

    # Applied promo code from Redis
    applied_code: Optional[str] = None
    try:
        applied_code = await redis.get(f"cart:promo:{user['id']}")
    except Exception:
        applied_code = None

    # Compute discount for applied code
    discount_result = await _compute_discount_for_code(db, user['id'], subtotal, estimated_shipping, applied_code)
    discount_total = discount_result["discount_total"]
    discounts_payload = [CartDiscount(**d) for d in discount_result["discounts"]]
    applied_promo_code = discount_result["applied_code"]

    estimated_total = subtotal + estimated_tax + estimated_shipping - discount_total
    if estimated_total < 0:
        estimated_total = Decimal('0.00')

    return Cart(
        items=cart_items,
        total_items=len(cart_items),
        subtotal=subtotal,
        discount_total=discount_total,
        applied_promo_code=applied_promo_code,
        discounts=discounts_payload,
        estimated_tax=estimated_tax,
        estimated_shipping=estimated_shipping,
        estimated_total=estimated_total
    )


@cart_router.get("/", response_model=Cart)
async def get_cart(user=Depends(get_current_user), db=Depends(get_db), redis=Depends(get_redis)):
    return await build_cart_response(user, db, redis)

@cart_router.get("/summary", response_model=CartSummary)
async def get_cart_summary(user=Depends(get_current_user), db=Depends(get_db)):
    query = """
        SELECT 
            COUNT(ci.id) as item_count,
            COALESCE(SUM(ci.quantity * p.price), 0) as subtotal
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id = $1 AND p.is_active = true
    """
    
    result = await db.fetchrow(query, user['id'])
    
    return CartSummary(
        item_count=result['item_count'],
        subtotal=result['subtotal'] or Decimal('0.00')
    )

@cart_router.post("/items", response_model=CartItem)
@limiter.limit("30/minute")
async def add_to_cart(
    item_data: CartItemCreate,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    # Check if product exists and is active
    product = await db.fetchrow(
        "SELECT id, name, price, slug, stock_quantity FROM products WHERE id = $1 AND is_active = true",
        item_data.product_id
    )
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check stock availability
    if product['stock_quantity'] < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product['stock_quantity']} items available in stock"
        )
    
    # Check if item already exists in cart
    existing_item = await db.fetchrow(
        "SELECT id, quantity FROM cart_items WHERE user_id = $1 AND product_id = $2",
        user['id'],
        item_data.product_id
    )
    
    if existing_item:
        # Update existing item quantity
        new_quantity = existing_item['quantity'] + item_data.quantity
        
        if new_quantity > product['stock_quantity']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add {item_data.quantity} more items. Only {product['stock_quantity']} available in stock"
            )
        
        if new_quantity > 99:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add more than 99 items to cart"
            )
        
        await db.execute(
            "UPDATE cart_items SET quantity = $1, updated_at = $2 WHERE id = $3",
            new_quantity,
            datetime.utcnow(),
            existing_item['id']
        )
        
        cart_item_id = existing_item['id']
    else:
        # Create new cart item
        cart_item = await db.fetchrow("""
            INSERT INTO cart_items (user_id, product_id, quantity, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """,
            user['id'],
            item_data.product_id,
            item_data.quantity,
            datetime.utcnow(),
            datetime.utcnow()
        )
        
        cart_item_id = cart_item['id']
    
    # Fetch the complete cart item data
    query = """
        SELECT 
            ci.id, ci.user_id, ci.product_id, ci.quantity, ci.created_at, ci.updated_at,
            p.name as product_name, p.price as product_price, p.slug as product_slug,
            p.stock_quantity, pi.url as product_image,
            (ci.quantity * p.price) as subtotal
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        LEFT JOIN product_images pi ON p.id = pi.product_id AND pi.is_primary = true
        WHERE ci.id = $1
    """
    
    cart_item_data = await db.fetchrow(query, cart_item_id)
    
    return CartItem(**dict(cart_item_data))

@cart_router.put("/items/{item_id}", response_model=CartItem)
async def update_cart_item(
    item_id: int,
    update_data: CartItemUpdate,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    # Check if cart item exists and belongs to user
    cart_item = await db.fetchrow(
        "SELECT id, product_id FROM cart_items WHERE id = $1 AND user_id = $2",
        item_id,
        user['id']
    )
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Check product stock
    product = await db.fetchrow(
        "SELECT stock_quantity FROM products WHERE id = $1 AND is_active = true",
        cart_item['product_id']
    )
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product['stock_quantity'] < update_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product['stock_quantity']} items available in stock"
        )
    
    # Update cart item
    await db.execute(
        "UPDATE cart_items SET quantity = $1, updated_at = $2 WHERE id = $3",
        update_data.quantity,
        datetime.utcnow(),
        item_id
    )
    
    # Fetch updated cart item data
    query = """
        SELECT 
            ci.id, ci.user_id, ci.product_id, ci.quantity, ci.created_at, ci.updated_at,
            p.name as product_name, p.price as product_price, p.slug as product_slug,
            p.stock_quantity, pi.url as product_image,
            (ci.quantity * p.price) as subtotal
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        LEFT JOIN product_images pi ON p.id = pi.product_id AND pi.is_primary = true
        WHERE ci.id = $1
    """
    
    cart_item_data = await db.fetchrow(query, item_id)
    
    return CartItem(**dict(cart_item_data))

@cart_router.delete("/items/{item_id}")
async def remove_cart_item(
    item_id: int,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    # Check if cart item exists and belongs to user
    result = await db.execute(
        "DELETE FROM cart_items WHERE id = $1 AND user_id = $2",
        item_id,
        user['id']
    )
    
    if result == "DELETE 0":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    return {"message": "Item removed from cart"}

@cart_router.delete("/")
async def clear_cart(user=Depends(get_current_user), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM cart_items WHERE user_id = $1",
        user['id']
    )
    
    return {"message": "Cart cleared"}

@cart_router.post("/sync")
@limiter.limit("10/minute")
async def sync_cart(
    cart_items: List[CartItemCreate],
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Sync local cart with server cart (for guest to authenticated user transition)"""
    
    # Clear existing cart
    await db.execute("DELETE FROM cart_items WHERE user_id = $1", user['id'])
    
    added_items = []
    
    for item_data in cart_items:
        try:
            # Check if product exists and is active
            product = await db.fetchrow(
                "SELECT id, stock_quantity FROM products WHERE id = $1 AND is_active = true",
                item_data.product_id
            )
            
            if not product:
                continue  # Skip invalid products
            
            # Adjust quantity if stock is insufficient
            quantity = min(item_data.quantity, product['stock_quantity'])
            if quantity <= 0:
                continue
            
            # Add item to cart
            cart_item = await db.fetchrow("""
                INSERT INTO cart_items (user_id, product_id, quantity, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """,
                user['id'],
                item_data.product_id,
                quantity,
                datetime.utcnow(),
                datetime.utcnow()
            )
            
            added_items.append(cart_item['id'])
            
        except Exception:
            continue  # Skip items that cause errors
    
    return {"message": f"Cart synced. {len(added_items)} items added."}
