import { authHeader } from "./auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export async function fetchAdminProducts({ page = 1, pageSize = 50, search = "", categoryId = null } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  if (search) params.append("search", search);
  if (categoryId) params.append("category_id", categoryId);

  const response = await fetch(`${API_BASE_URL}/admin/products?${params}`, {
    headers: { ...authHeader() },
  });

  if (!response.ok) {
    if (response.status === 401) throw new Error("Unauthorized");
    throw new Error("Failed to fetch admin catalogue");
  }
  return response.json();
}

export async function createAdminProduct(productData) {
  const response = await fetch(`${API_BASE_URL}/admin/products`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeader(),
    },
    body: JSON.stringify(productData),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to create product");
  }
  return response.json();
}

export async function updateAdminProduct(productId, updateData) {
  const response = await fetch(`${API_BASE_URL}/admin/products/${productId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...authHeader(),
    },
    body: JSON.stringify(updateData),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to update product");
  }
  return response.json();
}

export async function deactivateAdminProduct(productId) {
  const response = await fetch(`${API_BASE_URL}/admin/products/${productId}`, {
    method: "DELETE",
    headers: { ...authHeader() },
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to deactivate product");
  }
  return response.json();
}

export async function adjustProductStock(productId, delta, reason = "Manual adjustment") {
  const response = await fetch(`${API_BASE_URL}/admin/products/${productId}/stock`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeader(),
    },
    body: JSON.stringify({ quantity_delta: delta, reason }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to adjust stock");
  }
  return response.json();
}


export async function fetchAdminOrders(statusFilter = "") {
  const url = statusFilter
    ? `${API_BASE_URL}/admin/orders?status=${statusFilter}`
    : `${API_BASE_URL}/admin/orders`;

  const response = await fetch(url, {
    headers: { ...authHeader() },
  });

  if (!response.ok) {
    if (response.status === 401) throw new Error("Unauthorized");
    throw new Error("Failed to fetch customer orders");
  }
  return response.json();
}

export async function updateAdminOrderStatus(orderId, newStatus) {
  const response = await fetch(`${API_BASE_URL}/admin/orders/${orderId}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...authHeader(),
    },
    body: JSON.stringify({ status: newStatus }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to update order status");
  }
  return response.json();
}


export async function fetchAiForecasts(productId = null) {
  const url = productId
    ? `${API_BASE_URL}/admin/ai/forecasts?product_id=${productId}`
    : `${API_BASE_URL}/admin/ai/forecasts`;

  const response = await fetch(url, {
    headers: { ...authHeader() },
  });
  if (!response.ok) throw new Error("Failed to fetch AI forecasts");
  return response.json();
}

export async function fetchAiRecommendations() {
  const response = await fetch(`${API_BASE_URL}/admin/ai/recommendations`, {
    headers: { ...authHeader() },
  });
  if (!response.ok) throw new Error("Failed to fetch restock recommendations");
  return response.json();
}

export async function fetchAiExpiryAlerts() {
  const response = await fetch(`${API_BASE_URL}/admin/ai/expiry-alerts`, {
    headers: { ...authHeader() },
  });
  if (!response.ok) throw new Error("Failed to fetch expiry alerts");
  return response.json();
}


export async function fetchStoreAnalytics() {
  const response = await fetch(`${API_BASE_URL}/admin/analytics/summary`, {
    headers: { ...authHeader() },
  });
  if (!response.ok) throw new Error("Failed to fetch store analytics");
  return response.json();
}


// ── Sales History & Tracing ──

export async function fetchSalesHistory({ page = 1, pageSize = 25, dateFrom = null, dateTo = null } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize });
  if (dateFrom) params.append("date_from", dateFrom);
  if (dateTo) params.append("date_to", dateTo);

  const response = await fetch(`${API_BASE_URL}/admin/sales/history?${params}`, {
    headers: { ...authHeader() },
  });
  if (!response.ok) {
    if (response.status === 401) throw new Error("Unauthorized");
    throw new Error("Failed to fetch sales history");
  }
  return response.json();
}

export async function fetchDailySalesSummary(days = 30) {
  const response = await fetch(`${API_BASE_URL}/admin/sales/daily-summary?days=${days}`, {
    headers: { ...authHeader() },
  });
  if (!response.ok) throw new Error("Failed to fetch daily sales summary");
  return response.json();
}

export async function fetchProductSales(productId) {
  const response = await fetch(`${API_BASE_URL}/admin/sales/product/${productId}`, {
    headers: { ...authHeader() },
  });
  if (!response.ok) throw new Error("Failed to fetch product sales");
  return response.json();
}
