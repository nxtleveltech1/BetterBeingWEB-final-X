export const slugify = (text: string) =>
  text
    .toString()
    .toLowerCase()
    .replace(/\s+/g, "-") // Replace spaces with -
    .replace(/[^a-z0-9-]/g, "") // Remove all non-alphanum chars
    .replace(/-+/g, "-") // Collapse dashes
    .replace(/^-+|-+$/g, ""); // Trim -

export const getProductPath = (product: { id: number; name: string }) => {
  return `/product/${product.id}-${slugify(product.name)}`;
};

export const parseProductIdFromParam = (param: string | undefined): number => {
  if (!param) return 0;
  const match = String(param).match(/^(\d+)/);
  return match ? parseInt(match[1], 10) : 0;
};
