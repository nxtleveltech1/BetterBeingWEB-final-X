from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

from main import get_db, get_current_user, get_redis, limiter
from cart.cart_router import build_cart_response

promos_router = APIRouter(prefix="/api")


async def _fetch_discount_code(db, code: str) -> Optional[Dict[str, Any]]:
    row = await db.fetchrow(
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
    return dict(row) if row else None


async def _cart_subtotal(db, user_id: int) -> Decimal:
    subtotal = await db.fetchval(
        """
        SELECT COALESCE(SUM(ci.quantity * p.price), 0)
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id = $1 AND p.is_active = true
        """,
        user_id
    )
    return subtotal or Decimal('0.00')


@promos_router.post("/cart/apply-promo")
@limiter.limit("20/minute")
async def apply_promo(
    payload: Dict[str, str] = Body(...),
    user=Depends(get_current_user),
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    code = (payload.get("code") or "").strip()
    if not code:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Code is required")

    discount = await _fetch_discount_code(db, code)
    if not discount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or unknown code")

    # Validate active and time window
    now = datetime.utcnow()
    if not discount["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code is inactive")
    if discount["starts_at"] and now < discount["starts_at"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code not active yet")
    if discount["ends_at"] and now > discount["ends_at"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code has expired")
    if discount["usage_limit"] is not None and discount["used_count"] >= discount["usage_limit"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Code usage limit reached")

    # Enforce per-customer prior uses
    if discount["usage_limit_per_customer"] is not None and discount["usage_limit_per_customer"] > 0:
        used_by_customer = await db.fetchval(
            "SELECT COUNT(*) FROM discount_code_uses WHERE discount_code_id = $1 AND user_id = $2",
            discount["id"], user['id']
        )
        if used_by_customer and used_by_customer >= discount["usage_limit_per_customer"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already used this code")

    # Min order amount check against current cart subtotal
    subtotal = await _cart_subtotal(db, user['id'])
    if discount["minimum_order_amount"] is not None and subtotal < discount["minimum_order_amount"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart does not meet minimum order amount")

    # Persist applied code in Redis (7 days)
    await redis.setex(f"cart:promo:{user['id']}", 7 * 24 * 3600, discount["code"])

    # Return updated cart snapshot
    cart = await build_cart_response(user, db, redis)
    return {"cart": cart.model_dump()}


@promos_router.delete("/cart/remove-promo")
async def remove_promo(
    user=Depends(get_current_user),
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    await redis.delete(f"cart:promo:{user['id']}")
    cart = await build_cart_response(user, db, redis)
    return {"cart": cart.model_dump()}


@promos_router.get("/promos/active")
async def list_active_promos(
    scope: Optional[str] = Query(None, pattern="^(cart|product)$"),
    productId: Optional[int] = Query(None),
    categoryId: Optional[int] = Query(None),
    db=Depends(get_db)
):
    """List public, active promotions. Optionally filter by product/category for badges."""
    where = ["is_active = true", "(starts_at IS NULL OR NOW() >= starts_at)", "(ends_at IS NULL OR NOW() <= ends_at)"]
    params = []

    if scope == 'product':
        # Limit to promos that apply to all or specific target matching provided filters
        if productId is not None:
            where.append("(applies_to = 'all' OR (applies_to = 'specific_products' AND $1 = ANY(applicable_product_ids)))")
            params.append(productId)
        elif categoryId is not None:
            where.append("(applies_to = 'all' OR (applies_to = 'specific_categories' AND $1 = ANY(applicable_category_ids)))")
            params.append(categoryId)

    query = f"SELECT code, name, type, value, minimum_order_amount, maximum_discount_amount, applies_to, applicable_product_ids, applicable_category_ids, starts_at, ends_at FROM discount_codes WHERE {' AND '.join(where)} ORDER BY starts_at NULLS FIRST, name"
    rows = await db.fetch(query, *params)
    return {"promotions": [dict(r) for r in rows]}

