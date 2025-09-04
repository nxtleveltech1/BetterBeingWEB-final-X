"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import api from "@/services/apiOptimized";
import { useCartOptimized } from "@/contexts/CartContextOptimized";

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const { addToCart, isAddingToCart } = useCartOptimized();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["product", id],
    queryFn: () => api.getProduct(id),
    enabled: Number.isFinite(id),
  });

  if (!Number.isFinite(id)) return <div>Invalid product.</div>;
  if (isLoading) return <div>Loading…</div>;
  if (isError || !data) return <div>Product not found.</div>;

  const product: any = data;
  const hasDiscount = product.original_price && Number(product.original_price) > Number(product.price);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--color-neutral-50)] to-[var(--color-neutral-100)]">
      <div className="max-w-5xl mx-auto px-6 py-10 grid md:grid-cols-2 gap-10">
        <div className="rounded-2xl border border-[var(--color-neutral-200)] bg-white p-6">
          <div className="aspect-square bg-[var(--color-neutral-100)] rounded-xl" />
        </div>
        <div>
          <h1 className="text-3xl font-heading font-bold text-[var(--color-neutral-900)] mb-2">{product.name}</h1>
          <div className="mb-4">
            <span className="text-2xl font-bold text-[var(--bb-mahogany)]">R{product.price}</span>
            {hasDiscount && (
              <span className="ml-3 text-lg text-[var(--color-neutral-400)] line-through">R{product.original_price}</span>
            )}
          </div>

          {product.description && (
            <p className="text-[var(--color-neutral-700)] mb-6">{product.description}</p>
          )}

          <button
            onClick={() => addToCart({ productId: product.id, quantity: 1 })}
            disabled={isAddingToCart || !product.in_stock}
            className={`btn-primary px-6 py-3 ${!product.in_stock ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            {product.in_stock ? (isAddingToCart ? 'Adding…' : 'Add to Cart') : 'Out of stock'}
          </button>
        </div>
      </div>
    </div>
  );
}
