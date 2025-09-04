from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import asyncpg
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

from main import get_db, get_redis

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/products", tags=["products"])
limiter = Limiter(key_func=get_remote_address)

# Pydantic models
class ProductSize(BaseModel):
    size: str
    price: float
    original_price: Optional[float] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    original_price: Optional[float]
    image_url: str
    category_id: int
    subcategory_id: Optional[int]
    category_name: Optional[str]
    category_slug: Optional[str]
    subcategory_name: Optional[str]
    subcategory_slug: Optional[str]
    benefits: List[str]
    ingredients: List[str]
    tags: List[str]
    sizes: List[ProductSize]
    rating: float
    reviews_count: int
    in_stock: bool
    is_featured: bool
    is_popular: bool
    created_at: datetime

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    image_url: Optional[str]
    product_count: int
    subcategories: List[Dict[str, Any]]

class ProductsResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    limit: int
    offset: int
    search_term: Optional[str] = None

# Cache helper functions
async def get_cached_data(key: str, redis) -> Optional[Any]:
    if not redis:
        return None
    try:
        cached = await redis.get(key)
        if cached:
            return eval(cached)  # Use eval for simplicity, consider json.loads in production
    except Exception as e:
        logger.error(f"Cache get error: {e}")
    return None

async def set_cached_data(key: str, data: Any, ttl: int = 300, redis=None):
    if not redis:
        return False
    try:
        await redis.setex(key, ttl, str(data))
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False

@router.get("", response_model=ProductsResponse)
@limiter.limit("60/minute")
async def get_products(
    request: Request,
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    featured: Optional[bool] = Query(None),
    popular: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    """Get all products with filtering and pagination"""
    
    # Generate cache key
    cache_key = f"products:list:{category}:{subcategory}:{featured}:{popular}:{search}:{sort}:{limit}:{offset}:{price_min}:{price_max}"
    
    # Try to get from cache
    cached = await get_cached_data(cache_key, redis)
    if cached:
        logger.info(f"🎯 Cache hit: {cache_key}")
        return cached
    
    logger.info(f"❌ Cache miss: {cache_key}")
    
    try:
        if search:
            # Use search function if search term is provided
            result = await db.fetch("""
                SELECT * FROM search_products(
                    $1, $2, $3, $4, $5, TRUE, $6, $7, $8, $9
                )
            """, search, category, subcategory, featured, popular, price_min, price_max, limit, offset)
            
            # Get total count for search
            count_result = await db.fetchrow("""
                SELECT COUNT(*) as total
                FROM search_products($1, $2, $3, $4, $5, TRUE, $6, $7, 999999, 0)
            """, search, category, subcategory, featured, popular, price_min, price_max)
            
            total = count_result["total"] if count_result else 0
            
        else:
            # Build base query
            base_query = """
                WITH product_aggregates AS (
                    SELECT 
                        product_id,
                        array_agg(DISTINCT benefit) FILTER (WHERE benefit IS NOT NULL) as benefits,
                        array_agg(DISTINCT ingredient) FILTER (WHERE ingredient IS NOT NULL) as ingredients,
                        array_agg(DISTINCT tag) FILTER (WHERE tag IS NOT NULL) as tags,
                        json_agg(DISTINCT jsonb_build_object(
                            'size', size, 
                            'price', price, 
                            'original_price', original_price
                        )) FILTER (WHERE size IS NOT NULL) as sizes
                    FROM (
                        SELECT product_id, benefit, NULL as ingredient, NULL as tag, NULL as size, NULL as price, NULL as original_price FROM product_benefits
                        UNION ALL
                        SELECT product_id, NULL, ingredient, NULL, NULL, NULL, NULL FROM product_ingredients
                        UNION ALL
                        SELECT product_id, NULL, NULL, tag, NULL, NULL, NULL FROM product_tags
                        UNION ALL
                        SELECT product_id, NULL, NULL, NULL, size, price, original_price FROM product_sizes
                    ) combined
                    GROUP BY product_id
                )
                SELECT 
                    p.*,
                    c.name as category_name,
                    c.slug as category_slug,
                    sc.name as subcategory_name,
                    sc.slug as subcategory_slug,
                    COALESCE(pa.benefits, ARRAY[]::text[]) as benefits,
                    COALESCE(pa.ingredients, ARRAY[]::text[]) as ingredients,
                    COALESCE(pa.tags, ARRAY[]::text[]) as tags,
                    COALESCE(pa.sizes, '[]'::json) as sizes
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN subcategories sc ON p.subcategory_id = sc.id
                LEFT JOIN product_aggregates pa ON p.id = pa.product_id
                WHERE 1=1
            """
            
            query_params = []
            param_count = 0
            
            # Apply filters
            if category:
                param_count += 1
                base_query += f" AND c.slug = ${param_count}"
                query_params.append(category)
            
            if subcategory:
                param_count += 1
                base_query += f" AND sc.slug = ${param_count}"
                query_params.append(subcategory)
            
            if featured is not None:
                base_query += " AND p.is_featured = true"
            
            if popular is not None:
                base_query += " AND p.is_popular = true"
            
            if price_min is not None:
                param_count += 1
                base_query += f" AND p.price >= ${param_count}"
                query_params.append(price_min)
            
            if price_max is not None:
                param_count += 1
                base_query += f" AND p.price <= ${param_count}"
                query_params.append(price_max)
            
            # Add sorting
            if sort == "price-low":
                base_query += " ORDER BY p.price ASC"
            elif sort == "price-high":
                base_query += " ORDER BY p.price DESC"
            elif sort == "rating":
                base_query += " ORDER BY p.rating DESC, p.reviews_count DESC"
            elif sort == "popular":
                base_query += " ORDER BY p.reviews_count DESC, p.rating DESC"
            elif sort == "newest":
                base_query += " ORDER BY p.created_at DESC"
            else:
                base_query += " ORDER BY p.is_featured DESC, p.is_popular DESC, p.rating DESC, p.created_at DESC"
            
            # Add pagination
            param_count += 1
            base_query += f" LIMIT ${param_count}"
            query_params.append(limit)
            
            param_count += 1
            base_query += f" OFFSET ${param_count}"
            query_params.append(offset)
            
            # Execute query
            result = await db.fetch(base_query, *query_params)
            
            # Get total count
            count_query = """
                SELECT COUNT(DISTINCT p.id) as total
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN subcategories sc ON p.subcategory_id = sc.id
                WHERE 1=1
            """
            
            count_params = []
            count_param_num = 0
            
            if category:
                count_param_num += 1
                count_query += f" AND c.slug = ${count_param_num}"
                count_params.append(category)
            
            if subcategory:
                count_param_num += 1
                count_query += f" AND sc.slug = ${count_param_num}"
                count_params.append(subcategory)
            
            if featured is not None:
                count_query += " AND p.is_featured = true"
            
            if popular is not None:
                count_query += " AND p.is_popular = true"
            
            if price_min is not None:
                count_param_num += 1
                count_query += f" AND p.price >= ${count_param_num}"
                count_params.append(price_min)
            
            if price_max is not None:
                count_param_num += 1
                count_query += f" AND p.price <= ${count_param_num}"
                count_params.append(price_max)
            
            count_result = await db.fetchrow(count_query, *count_params)
            total = count_result["total"] if count_result else 0
        
        # Format response
        response = {
            "products": result,
            "total": total,
            "limit": limit,
            "offset": offset,
            "search_term": search
        }
        
        # Cache the response
        await set_cached_data(cache_key, response, redis=redis)
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch products"
        )

@router.get("/categories", response_model=Dict[str, Any])
@limiter.limit("60/minute")
async def get_categories(
    request: Request,
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    """Get all categories with product counts"""
    
    cache_key = "categories:all"
    
    # Try to get from cache
    cached = await get_cached_data(cache_key, redis)
    if cached:
        logger.info(f"🎯 Cache hit: {cache_key}")
        return {"categories": cached}
    
    logger.info(f"❌ Cache miss: {cache_key}")
    
    try:
        query = """
            WITH category_counts AS (
                SELECT
                    c.id,
                    COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id AND p.in_stock = true
                GROUP BY c.id
            ),
            subcategory_counts AS (
                SELECT
                    sc.category_id,
                    json_agg(
                        json_build_object(
                            'id', sc.id,
                            'name', sc.name,
                            'slug', sc.slug,
                            'description', sc.description,
                            'product_count', COUNT(p.id)
                        )
                        ORDER BY sc.name
                    ) as subcategories
                FROM subcategories sc
                LEFT JOIN products p ON sc.id = p.subcategory_id AND p.in_stock = true
                GROUP BY sc.category_id
            )
            SELECT
                c.*,
                cc.product_count,
                COALESCE(scc.subcategories, '[]'::json) as subcategories
            FROM categories c
            LEFT JOIN category_counts cc ON c.id = cc.id
            LEFT JOIN subcategory_counts scc ON c.id = scc.category_id
            ORDER BY c.name
        """
        
        result = await db.fetch(query)
        
        # Cache the result
        await set_cached_data(cache_key, result, redis=redis)
        
        return {"categories": result}
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch categories"
        )

@router.get("/{product_id}", response_model=ProductResponse)
@limiter.limit("60/minute")
async def get_product(
    request: Request,
    product_id: int,
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    """Get single product by ID"""
    
    cache_key = f"product:{product_id}"
    
    # Try to get from cache
    cached = await get_cached_data(cache_key, redis)
    if cached:
        logger.info(f"🎯 Cache hit: {cache_key}")
        return cached
    
    logger.info(f"❌ Cache miss: {cache_key}")
    
    try:
        query = """
            WITH product_data AS (
                SELECT
                    p.*,
                    c.name as category_name,
                    c.slug as category_slug,
                    sc.name as subcategory_name,
                    sc.slug as subcategory_slug
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN subcategories sc ON p.subcategory_id = sc.id
                WHERE p.id = $1
            ),
            product_benefits AS (
                SELECT array_agg(benefit) as benefits
                FROM product_benefits
                WHERE product_id = $1
            ),
            product_ingredients AS (
                SELECT array_agg(ingredient) as ingredients
                FROM product_ingredients
                WHERE product_id = $1
            ),
            product_tags AS (
                SELECT array_agg(tag) as tags
                FROM product_tags
                WHERE product_id = $1
            ),
            product_sizes AS (
                SELECT json_agg(jsonb_build_object(
                    'size', size,
                    'price', price,
                    'original_price', original_price
                )) as sizes
                FROM product_sizes
                WHERE product_id = $1
            ),
            recent_reviews AS (
                SELECT
                    json_agg(
                        jsonb_build_object(
                            'id', r.id,
                            'rating', r.rating,
                            'title', r.title,
                            'comment', r.comment,
                            'created_at', r.created_at,
                            'user_name', COALESCE(u.first_name || ' ' || u.last_name, 'Anonymous'),
                            'is_verified', r.is_verified_purchase
                        )
                        ORDER BY r.created_at DESC
                    ) as recent_reviews
                FROM reviews r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.product_id = $1
                LIMIT 5
            )
            SELECT
                pd.*,
                COALESCE(pb.benefits, ARRAY[]::text[]) as benefits,
                COALESCE(pi.ingredients, ARRAY[]::text[]) as ingredients,
                COALESCE(pt.tags, ARRAY[]::text[]) as tags,
                COALESCE(ps.sizes, '[]'::json) as sizes,
                COALESCE(rr.recent_reviews, '[]'::json) as recent_reviews
            FROM product_data pd
            CROSS JOIN product_benefits pb
            CROSS JOIN product_ingredients pi
            CROSS JOIN product_tags pt
            CROSS JOIN product_sizes ps
            CROSS JOIN recent_reviews rr
        """
        
        result = await db.fetchrow(query, product_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        
        # Cache the result
        await set_cached_data(cache_key, result, redis=redis)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching product: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch product"
        )

@router.get("/{product_id}/related", response_model=Dict[str, Any])
@limiter.limit("60/minute")
async def get_related_products(
    request: Request,
    product_id: int,
    limit: int = Query(4, ge=1, le=20),
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    """Get related products"""
    
    cache_key = f"related_products:{product_id}:{limit}"
    
    # Try to get from cache
    cached = await get_cached_data(cache_key, redis)
    if cached:
        logger.info(f"🎯 Cache hit: {cache_key}")
        return {"products": cached, "count": len(cached)}
    
    logger.info(f"❌ Cache miss: {cache_key}")
    
    try:
        # Get the current product's category and tags
        product_query = """
            SELECT
                p.category_id,
                p.subcategory_id,
                array_agg(DISTINCT pt.tag) as tags,
                array_agg(DISTINCT pb.benefit) as benefits,
                array_agg(DISTINCT pi.ingredient) as ingredients
            FROM products p
            LEFT JOIN product_tags pt ON p.id = pt.product_id
            LEFT JOIN product_benefits pb ON p.id = pb.product_id
            LEFT JOIN product_ingredients pi ON p.id = pi.product_id
            WHERE p.id = $1
            GROUP BY p.id, p.category_id, p.subcategory_id
        """
        
        product_result = await db.fetchrow(product_query, product_id)
        
        if not product_result:
            return {"products": [], "count": 0}
        
        # Find related products
        related_query = """
            WITH product_similarity AS (
                SELECT
                    p.*,
                    c.name as category_name,
                    c.slug as category_slug,
                    sc.name as subcategory_name,
                    sc.slug as subcategory_slug,
                    CASE
                        WHEN p.category_id = $2 THEN 3
                        WHEN p.subcategory_id = $3 THEN 2
                        ELSE 1
                    END as relevance_score,
                    array_agg(DISTINCT pt.tag) as tags,
                    array_agg(DISTINCT pb.benefit) as benefits,
                    array_agg(DISTINCT pi.ingredient) as ingredients
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN subcategories sc ON p.subcategory_id = sc.id
                LEFT JOIN product_tags pt ON p.id = pt.product_id
                LEFT JOIN product_benefits pb ON p.id = pb.product_id
                LEFT JOIN product_ingredients pi ON p.id = pi.product_id
                WHERE p.id != $1
                    AND p.in_stock = true
                    AND (
                        p.category_id = $2
                        OR p.subcategory_id = $3
                        OR EXISTS (
                            SELECT 1 FROM product_tags
                            WHERE product_id = p.id AND tag = ANY($4)
                        )
                        OR EXISTS (
                            SELECT 1 FROM product_benefits
                            WHERE product_id = p.id AND benefit = ANY($5)
                        )
                    )
                GROUP BY p.id, c.name, c.slug, sc.name, sc.slug
                ORDER BY relevance_score DESC, p.rating DESC, p.reviews_count DESC
                LIMIT $6
            )
            SELECT
                ps.*,
                COALESCE(ps.tags, ARRAY[]::text[]) as tags,
                COALESCE(ps.benefits, ARRAY[]::text[]) as benefits,
                COALESCE(ps.ingredients, ARRAY[]::text[]) as ingredients
            FROM product_similarity ps
        """
        
        related_result = await db.fetch(related_query, [
            product_id,
            product_result["category_id"],
            product_result["subcategory_id"],
            product_result["tags"] or [],
            product_result["benefits"] or [],
            limit
        ])
        
        # Cache the result
        await set_cached_data(cache_key, related_result, redis=redis)
        
        return {
            "products": related_result,
            "count": len(related_result)
        }
        
    except Exception as e:
        logger.error(f"Error fetching related products: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch related products"
        )