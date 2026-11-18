const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export async function checkApiHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) throw new Error("API health check failed");
  return response.json();
}

export async function fetchCategories() {
  const response = await fetch(`${API_BASE_URL}/categories`);
  if (!response.ok) throw new Error("Failed to fetch categories");
  return response.json();
}

export async function fetchProducts({ page = 1, pageSize = 20, categoryId = null, search = "" } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  if (categoryId) params.append("category_id", categoryId);
  if (search) params.append("search", search);
  const response = await fetch(`${API_BASE_URL}/products?${params}`);
  if (!response.ok) throw new Error("Failed to fetch products");
  return response.json();
}

export async function fetchProductBySlug(slug) {
  const response = await fetch(`${API_BASE_URL}/products/${slug}`);
  if (response.status === 404) return null;
  if (!response.ok) throw new Error("Failed to fetch product");
  return response.json();
}

export async function fetchProductReviews(productId, { page = 1, pageSize = 10 } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  const response = await fetch(`${API_BASE_URL}/products/${productId}/reviews?${params}`);
  if (!response.ok) throw new Error("Failed to fetch reviews");
  return response.json();
}

export async function submitReview(productId, { rating, body }) {
  const response = await fetch(`${API_BASE_URL}/products/${productId}/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating, body }),
  });
  if (!response.ok) throw new Error("Failed to submit review");
  return response.json();
}
