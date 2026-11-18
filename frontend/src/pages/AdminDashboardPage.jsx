import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Shield, LogOut, Plus, Search, RefreshCw, Package,
  AlertTriangle, Tag, CheckCircle2, X, ShoppingBag,
  Sparkles, TrendingUp, AlertCircle, Info, Calendar,
  BarChart3, DollarSign, PieChart
} from "lucide-react";
import { getStoredAdmin, isAuthenticated, logoutAdmin } from "../services/auth";
import {
  fetchAdminProducts,
  createAdminProduct,
  updateAdminProduct,
  deactivateAdminProduct,
  adjustProductStock,
  fetchAdminOrders,
  updateAdminOrderStatus,
  fetchAiForecasts,
  fetchAiRecommendations,
  fetchAiExpiryAlerts,
  fetchStoreAnalytics,
} from "../services/adminApi";
import { fetchCategories } from "../services/api";

export default function AdminDashboardPage() {
  const navigate = useNavigate();
  const [admin, setAdmin] = useState(null);
  const [activeTab, setActiveTab] = useState("products"); // 'products' | 'orders' | 'ai' | 'analytics'
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [categories, setCategories] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [expiryAlerts, setExpiryAlerts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedAiProdId, setSelectedAiProdId] = useState("");

  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [orderStatusFilter, setOrderStatusFilter] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [actionMessage, setActionMessage] = useState("");

  // New product form state
  const [newProd, setNewProd] = useState({
    name: "", slug: "", sku: "", description: "",
    selling_price: "", cost_price: "", unit: "pcs",
    category_id: "", initial_stock: 50, reorder_level: 10,
    quality_notes: "", expiry_info: ""
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === "products") {
        const [prodsData, catsData] = await Promise.all([
          fetchAdminProducts({ search, categoryId: selectedCategory || null }),
          fetchCategories(),
        ]);
        setProducts(prodsData);
        setCategories(catsData);
      } else if (activeTab === "orders") {
        const ordersData = await fetchAdminOrders(orderStatusFilter);
        setOrders(ordersData);
      } else if (activeTab === "ai") {
        const [fcData, recData, expData] = await Promise.all([
          fetchAiForecasts(selectedAiProdId || null),
          fetchAiRecommendations(),
          fetchAiExpiryAlerts(),
        ]);
        setForecasts(Array.isArray(fcData) ? fcData : [fcData]);
        setRecommendations(recData);
        setExpiryAlerts(expData);
      } else if (activeTab === "analytics") {
        const analyticsData = await fetchStoreAnalytics();
        setAnalytics(analyticsData);
      }
    } catch (err) {
      if (err.message === "Unauthorized") {
        logoutAdmin();
        navigate("/admin/login");
      }
    } finally {
      setLoading(false);
    }
  }, [activeTab, search, selectedCategory, orderStatusFilter, selectedAiProdId, navigate]);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/admin/login");
      return;
    }
    setAdmin(getStoredAdmin());
    loadData();
  }, [loadData, navigate]);

  const handleLogout = async () => {
    await logoutAdmin();
    navigate("/admin/login");
  };

  const handleStockAdjust = async (productId, delta) => {
    try {
      await adjustProductStock(productId, delta, "Admin quick adjustment");
      setActionMessage(`Stock updated (${delta > 0 ? "+" + delta : delta})`);
      setTimeout(() => setActionMessage(""), 3000);
      loadData();
    } catch (err) {
      alert("Failed to adjust stock: " + err.message);
    }
  };

  const handleToggleActive = async (product) => {
    try {
      if (product.is_active) {
        await deactivateAdminProduct(product.id);
        setActionMessage(`"${product.name}" deactivated`);
      } else {
        await updateAdminProduct(product.id, { is_active: true });
        setActionMessage(`"${product.name}" reactivated`);
      }
      setTimeout(() => setActionMessage(""), 3000);
      loadData();
    } catch (err) {
      alert("Failed to update status: " + err.message);
    }
  };

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await updateAdminOrderStatus(orderId, newStatus);
      setActionMessage(`Order #${orderId} marked as ${newStatus}`);
      setTimeout(() => setActionMessage(""), 3000);
      loadData();
    } catch (err) {
      alert("Failed to update order status: " + err.message);
    }
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        name: newProd.name.trim(),
        slug: newProd.slug.trim() || newProd.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
        sku: newProd.sku.trim(),
        description: newProd.description.trim() || null,
        selling_price: parseFloat(newProd.selling_price),
        cost_price: newProd.cost_price ? parseFloat(newProd.cost_price) : null,
        unit: newProd.unit.trim() || "pcs",
        category_id: newProd.category_id ? parseInt(newProd.category_id) : null,
        initial_stock: parseInt(newProd.initial_stock) || 0,
        reorder_level: parseInt(newProd.reorder_level) || 10,
        quality_notes: newProd.quality_notes.trim() || null,
        expiry_info: newProd.expiry_info.trim() || null,
      };

      await createAdminProduct(payload);
      setShowAddModal(false);
      setActionMessage(`Product "${payload.name}" created successfully!`);
      setTimeout(() => setActionMessage(""), 3000);
      setNewProd({
        name: "", slug: "", sku: "", description: "",
        selling_price: "", cost_price: "", unit: "pcs",
        category_id: "", initial_stock: 50, reorder_level: 10,
        quality_notes: "", expiry_info: ""
      });
      loadData();
    } catch (err) {
      alert("Failed to create product: " + err.message);
    }
  };

  // Metrics
  const activeCount = products.filter(p => p.is_active).length;
  const lowStockCount = products.filter(p => (p.inventory?.quantity ?? 0) <= (p.inventory?.reorder_level ?? 10)).length;

  return (
    <div className="admin-dashboard">
      {/* Top Navbar */}
      <div className="admin-topbar">
        <div className="admin-brand-section">
          <Shield className="admin-brand-icon" size={24} />
          <div>
            <h2>Store Operations Workspace</h2>
            <p className="admin-user-subtitle">
              Logged in as <strong>{admin?.full_name || "Admin"}</strong> ({admin?.email})
            </p>
          </div>
        </div>

        <div className="admin-actions-bar">
          {activeTab === "products" && (
            <button className="primary-button add-prod-btn" onClick={() => setShowAddModal(true)}>
              <Plus size={16} /> Add Product
            </button>
          )}
          <button className="admin-logout-btn" onClick={handleLogout} title="Sign Out">
            <LogOut size={16} /> Sign Out
          </button>
        </div>
      </div>

      {actionMessage && (
        <div className="admin-toast-banner">
          <CheckCircle2 size={16} /> {actionMessage}
        </div>
      )}

      {/* Tabs */}
      <div className="admin-nav-tabs">
        <button
          className={`tab-btn ${activeTab === "products" ? "active" : ""}`}
          onClick={() => setActiveTab("products")}
        >
          <Package size={16} /> Products & Inventory
        </button>
        <button
          className={`tab-btn ${activeTab === "orders" ? "active" : ""}`}
          onClick={() => setActiveTab("orders")}
        >
          <ShoppingBag size={16} /> Customer Orders
        </button>
        <button
          className={`tab-btn ${activeTab === "ai" ? "active" : ""}`}
          onClick={() => setActiveTab("ai")}
        >
          <Sparkles size={16} /> AI Intelligence & Forecasts
        </button>
        <button
          className={`tab-btn ${activeTab === "analytics" ? "active" : ""}`}
          onClick={() => setActiveTab("analytics")}
        >
          <BarChart3 size={16} /> Sales & Margin Analytics
        </button>
      </div>

      {/* TAB 1: PRODUCTS */}
      {activeTab === "products" && (
        <>
          <div className="admin-kpi-grid">
            <div className="kpi-card">
              <div className="kpi-icon-wrap green"><Package size={20} /></div>
              <div>
                <span className="kpi-label">Active Catalogue</span>
                <div className="kpi-value">{activeCount} / {products.length}</div>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon-wrap amber"><AlertTriangle size={20} /></div>
              <div>
                <span className="kpi-label">Low Stock Alerts</span>
                <div className="kpi-value">{lowStockCount} items</div>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon-wrap blue"><Tag size={20} /></div>
              <div>
                <span className="kpi-label">Categories</span>
                <div className="kpi-value">{categories.length} active</div>
              </div>
            </div>
          </div>

          <div className="admin-toolbar">
            <div className="admin-search-box">
              <Search size={16} className="search-icon" />
              <input
                type="text"
                placeholder="Search catalogue by name or SKU…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <select
              className="admin-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">All Categories</option>
              {categories.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>

            <button className="admin-refresh-btn" onClick={loadData} title="Refresh Catalogue">
              <RefreshCw size={15} />
            </button>
          </div>

          <div className="admin-table-container">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Product / SKU</th>
                  <th>Category</th>
                  <th>Selling Price</th>
                  <th>Cost Price (Admin)</th>
                  <th>Gross Margin</th>
                  <th>Current Stock</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="8" className="table-loading">Loading inventory…</td></tr>
                ) : products.length === 0 ? (
                  <tr><td colSpan="8" className="table-empty">No products matched the search.</td></tr>
                ) : (
                  products.map((p) => {
                    const sell = Number(p.selling_price);
                    const cost = p.cost_price ? Number(p.cost_price) : null;
                    const margin = cost ? (((sell - cost) / sell) * 100).toFixed(1) : null;
                    const qty = p.inventory?.quantity ?? 0;
                    const isLow = qty <= (p.inventory?.reorder_level ?? 10);

                    return (
                      <tr key={p.id} className={!p.is_active ? "row-inactive" : ""}>
                        <td>
                          <div className="prod-cell">
                            <strong>{p.name}</strong>
                            <span className="sku-tag">SKU: {p.sku}</span>
                          </div>
                        </td>
                        <td>{p.category?.name || "Uncategorized"}</td>
                        <td><strong>₹{sell.toFixed(2)}</strong> {p.unit && <span className="unit-label">/ {p.unit}</span>}</td>
                        <td className="cost-cell">{cost ? `₹${cost.toFixed(2)}` : "—"}</td>
                        <td>
                          {margin ? (
                            <span className={`margin-badge ${margin >= 30 ? "high" : "normal"}`}>
                              {margin}%
                            </span>
                          ) : "—"}
                        </td>
                        <td>
                          <div className="stock-cell">
                            <span className={`stock-count ${isLow ? "low" : ""}`}>
                              {qty}
                            </span>
                            <div className="stock-btn-group">
                              <button onClick={() => handleStockAdjust(p.id, -10)} title="Deduct 10 units">-10</button>
                              <button onClick={() => handleStockAdjust(p.id, 10)} title="Add 10 units">+10</button>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`status-pill ${p.is_active ? "active" : "inactive"}`}>
                            {p.is_active ? "Active" : "Disabled"}
                          </span>
                        </td>
                        <td>
                          <button
                            className="toggle-status-btn"
                            onClick={() => handleToggleActive(p)}
                            title={p.is_active ? "Deactivate product" : "Reactivate product"}
                          >
                            {p.is_active ? "Deactivate" : "Activate"}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* TAB 2: ORDERS */}
      {activeTab === "orders" && (
        <div className="admin-orders-view">
          <div className="admin-toolbar">
            <select
              className="admin-select"
              value={orderStatusFilter}
              onChange={(e) => setOrderStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="confirmed">Confirmed</option>
              <option value="out_for_delivery">Out for Delivery</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>

            <button className="admin-refresh-btn" onClick={loadData} title="Refresh Orders">
              <RefreshCw size={15} />
            </button>
          </div>

          <div className="admin-table-container">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Order Ref</th>
                  <th>Customer</th>
                  <th>Items Purchased</th>
                  <th>Delivery Address</th>
                  <th>Total Amount</th>
                  <th>Current Status</th>
                  <th>Update Status</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="7" className="table-loading">Loading customer orders…</td></tr>
                ) : orders.length === 0 ? (
                  <tr><td colSpan="7" className="table-empty">No orders found.</td></tr>
                ) : (
                  orders.map((o) => (
                    <tr key={o.id}>
                      <td>
                        <strong>{o.order_number}</strong>
                        <div className="order-time-sub">
                          {new Date(o.created_at).toLocaleDateString()} {new Date(o.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </td>
                      <td>
                        <strong>{o.customer_name}</strong>
                        <div className="order-contact-sub">{o.customer_phone}</div>
                      </td>
                      <td>
                        <div className="order-items-snippet">
                          {o.items.map((it) => (
                            <span key={it.id} className="order-chip">
                              {it.product_name_snapshot} × {it.quantity}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="address-col">{o.delivery_address}</td>
                      <td><strong>₹{Number(o.total_amount).toFixed(2)}</strong></td>
                      <td>
                        <span className={`status-pill ${o.status}`}>
                          {o.status.replace("_", " ").toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <select
                          className="admin-status-dropdown"
                          value={o.status}
                          onChange={(e) => handleStatusChange(o.id, e.target.value)}
                        >
                          <option value="pending">Pending</option>
                          <option value="confirmed">Confirmed</option>
                          <option value="out_for_delivery">Out for Delivery</option>
                          <option value="delivered">Delivered</option>
                          <option value="cancelled">Cancelled (Restore Stock)</option>
                        </select>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: AI INTELLIGENCE & FORECASTING */}
      {activeTab === "ai" && (
        <div className="admin-ai-view">
          <div className="ai-mandatory-disclaimer">
            <Info size={16} />
            <div>
              <strong>Advisory Invariant:</strong> AI forecasts and suggestions are statistical estimates to assist store decisions.
              They never automatically change inventory counts, pricing, or purchase orders.
            </div>
          </div>

          {/* Section 1: Demand Forecasts */}
          <div className="ai-section-card">
            <div className="ai-section-header">
              <div className="ai-section-title">
                <TrendingUp size={20} className="icon-green" />
                <h3>7-Day Demand Forecasting</h3>
              </div>
              <button className="admin-refresh-btn" onClick={loadData} title="Re-run ML Forecasts">
                <RefreshCw size={14} /> Refresh Forecasts
              </button>
            </div>

            <div className="forecasts-grid">
              {loading ? (
                <div className="table-loading">Running forecasting models…</div>
              ) : forecasts.length === 0 ? (
                <p>No product forecasts available.</p>
              ) : (
                forecasts.map((fc) => (
                  <div key={fc.product_id} className="forecast-card">
                    <div className="fc-header">
                      <div>
                        <h4>{fc.product_name}</h4>
                        <span className="sku-tag">SKU: {fc.sku}</span>
                      </div>
                      <div className="fc-prediction-stat">
                        <span className="fc-stat-number">{fc.predicted_demand_7d}</span>
                        <span className="fc-stat-label">Units / 7 Days</span>
                      </div>
                    </div>

                    <div className="fc-meta-row">
                      <span className="fc-meta-pill">Model: {fc.model_name}</span>
                      {fc.baseline_mae !== null && (
                        <span className="fc-meta-pill">MAE: {fc.baseline_mae}</span>
                      )}
                    </div>

                    {fc.status_message && (
                      <div className="fc-status-note">
                        <Info size={12} /> {fc.status_message}
                      </div>
                    )}

                    {/* Mini Bar Chart */}
                    <div className="fc-chart-container">
                      <div className="fc-chart-bars">
                        {fc.daily_forecast?.map((day) => {
                          const maxVal = Math.max(...fc.daily_forecast.map(d => d.predicted_units), 5);
                          const barHeight = Math.max(12, (day.predicted_units / maxVal) * 60);
                          return (
                            <div key={day.date} className="fc-bar-column">
                              <span className="bar-val">{day.predicted_units}</span>
                              <div className="bar-fill" style={{ height: `${barHeight}px` }} />
                              <span className="bar-day">{day.day_of_week}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Section 2: Smart Restock Recommendations */}
          <div className="ai-section-card">
            <div className="ai-section-header">
              <div className="ai-section-title">
                <Package size={20} className="icon-amber" />
                <h3>Intelligent Restock Recommendations</h3>
              </div>
            </div>

            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Current Stock</th>
                    <th>Sales Velocity</th>
                    <th>Days of Supply</th>
                    <th>Urgency Level</th>
                    <th>Recommended Order</th>
                    <th>Reason / Diagnosis</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {recommendations.length === 0 ? (
                    <tr><td colSpan="8" className="table-empty">Inventory is fully balanced.</td></tr>
                  ) : (
                    recommendations.map((rec) => (
                      <tr key={rec.product_id} className={rec.urgency === "immediate" ? "row-urgent" : ""}>
                        <td>
                          <strong>{rec.product_name}</strong>
                          <span className="sku-tag"> ({rec.category_name})</span>
                        </td>
                        <td><strong>{rec.current_stock}</strong></td>
                        <td>{rec.daily_velocity} units/day</td>
                        <td>
                          <span className={`days-badge ${rec.days_of_supply <= 2 ? "critical" : rec.days_of_supply <= 5 ? "warning" : "ok"}`}>
                            {rec.days_of_supply} days
                          </span>
                        </td>
                        <td>
                          <span className={`urgency-pill ${rec.urgency}`}>
                            {rec.urgency.toUpperCase()}
                          </span>
                        </td>
                        <td>
                          {rec.suggested_reorder_quantity > 0 ? (
                            <strong className="reorder-qty">+{rec.suggested_reorder_quantity} units</strong>
                          ) : (
                            <span className="reorder-none">—</span>
                          )}
                        </td>
                        <td className="reason-col">{rec.reason}</td>
                        <td>
                          {rec.suggested_reorder_quantity > 0 && (
                            <button
                              className="quick-restock-btn"
                              onClick={() => handleStockAdjust(rec.product_id, rec.suggested_reorder_quantity)}
                              title="Restock suggested batch immediately"
                            >
                              Restock +{rec.suggested_reorder_quantity}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 3: Freshness & Perishable Alerts */}
          <div className="ai-section-card">
            <div className="ai-section-header">
              <div className="ai-section-title">
                <Calendar size={20} className="icon-blue" />
                <h3>Perishable Freshness & Shelf-Life Watchlist</h3>
              </div>
            </div>
            <p className="ai-disclaimer-sub">
              * Freshness windows are derived from store-declared shelf life metadata and supplier packing dates. Not independently lab-certified.
            </p>

            <div className="expiry-cards-grid">
              {expiryAlerts.map((exp) => (
                <div key={exp.product_id} className={`expiry-alert-card ${exp.alert_level}`}>
                  <div className="exp-card-header">
                    <h4>{exp.product_name}</h4>
                    <span className={`exp-badge ${exp.alert_level}`}>
                      {exp.shelf_life_window_days} Days Window
                    </span>
                  </div>
                  <div className="exp-card-body">
                    <p className="exp-notes"><strong>Declared Shelf Life:</strong> {exp.store_expiry_info}</p>
                    <p className="exp-quality"><strong>Quality Details:</strong> {exp.store_quality_notes}</p>
                    <div className="exp-advice">
                      <AlertCircle size={13} />
                      <span>{exp.action_advice}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: SALES & MARGIN ANALYTICS */}
      {activeTab === "analytics" && (
        <div className="admin-analytics-view">
          <div className="admin-toolbar">
            <button className="admin-refresh-btn" onClick={loadData} title="Refresh Analytics">
              <RefreshCw size={14} /> Refresh Analytics
            </button>
          </div>

          {loading || !analytics ? (
            <div className="table-loading">Computing business metrics & inventory valuation…</div>
          ) : (
            <>
              {/* Financial KPIs */}
              <div className="admin-kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-icon-wrap green"><DollarSign size={22} /></div>
                  <div>
                    <span className="kpi-label">Total Realized Revenue</span>
                    <div className="kpi-value">₹{analytics.sales_summary.total_revenue.toFixed(2)}</div>
                    <span className="kpi-subtext">{analytics.sales_summary.total_orders} total orders placed</span>
                  </div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-icon-wrap blue"><TrendingUp size={22} /></div>
                  <div>
                    <span className="kpi-label">Potential Gross Profit</span>
                    <div className="kpi-value">₹{analytics.inventory_valuation.potential_gross_profit.toFixed(2)}</div>
                    <span className="kpi-subtext">Overall Margin: <strong>{analytics.inventory_valuation.overall_gross_margin_pct}%</strong></span>
                  </div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-icon-wrap amber"><Package size={22} /></div>
                  <div>
                    <span className="kpi-label">Total Inventory Retail Value</span>
                    <div className="kpi-value">₹{analytics.inventory_valuation.total_retail_value.toFixed(2)}</div>
                    <span className="kpi-subtext">{analytics.inventory_valuation.total_stock_units} units on shelf (Cost: ₹{analytics.inventory_valuation.total_cost_value.toFixed(2)})</span>
                  </div>
                </div>
              </div>

              {/* Top Selling Products & Order Status Breakdown */}
              <div className="analytics-details-grid">
                <div className="ai-section-card">
                  <div className="ai-section-header">
                    <div className="ai-section-title">
                      <BarChart3 size={20} className="icon-green" />
                      <h3>Top Selling Products by Volume</h3>
                    </div>
                  </div>

                  {analytics.top_selling_products.length === 0 ? (
                    <p className="table-empty">No sales recorded yet. Place orders to see sales metrics!</p>
                  ) : (
                    <div className="top-sellers-list">
                      {analytics.top_selling_products.map((item, idx) => (
                        <div key={item.product_name} className="top-seller-row">
                          <div className="top-seller-rank">{idx + 1}</div>
                          <div className="top-seller-info">
                            <strong>{item.product_name}</strong>
                            <span>{item.units_sold} units sold</span>
                          </div>
                          <div className="top-seller-rev">
                            ₹{item.revenue.toFixed(2)}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="ai-section-card">
                  <div className="ai-section-header">
                    <div className="ai-section-title">
                      <PieChart size={20} className="icon-blue" />
                      <h3>Order Status Distribution</h3>
                    </div>
                  </div>

                  <div className="status-distribution-grid">
                    {Object.entries(analytics.sales_summary.orders_by_status).map(([st, cnt]) => (
                      <div key={st} className="status-dist-item">
                        <span className={`status-pill ${st}`}>{st.replace("_", " ").toUpperCase()}</span>
                        <strong>{cnt} order{cnt !== 1 ? "s" : ""}</strong>
                      </div>
                    ))}
                    {Object.keys(analytics.sales_summary.orders_by_status).length === 0 && (
                      <p className="table-empty">No order distribution data yet.</p>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Add Product Modal */}
      {showAddModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>Add New Product to Inventory</h3>
              <button className="modal-close-btn" onClick={() => setShowAddModal(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleCreateProduct} className="modal-form">
              <div className="form-row-2">
                <div className="form-group">
                  <label>Product Name *</label>
                  <input
                    type="text" required
                    placeholder="e.g. Organic Strawberries"
                    value={newProd.name}
                    onChange={(e) => setNewProd({...newProd, name: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>SKU (Stock Keeping Unit) *</label>
                  <input
                    type="text" required
                    placeholder="e.g. FV-099"
                    value={newProd.sku}
                    onChange={(e) => setNewProd({...newProd, sku: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-row-2">
                <div className="form-group">
                  <label>Selling Price (₹) *</label>
                  <input
                    type="number" step="0.01" min="0.01" required
                    placeholder="120.00"
                    value={newProd.selling_price}
                    onChange={(e) => setNewProd({...newProd, selling_price: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Cost Price (₹ - Admin internal)</label>
                  <input
                    type="number" step="0.01" min="0"
                    placeholder="75.00"
                    value={newProd.cost_price}
                    onChange={(e) => setNewProd({...newProd, cost_price: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-row-3">
                <div className="form-group">
                  <label>Unit</label>
                  <input
                    type="text"
                    placeholder="kg, pcs, 500g"
                    value={newProd.unit}
                    onChange={(e) => setNewProd({...newProd, unit: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <select
                    value={newProd.category_id}
                    onChange={(e) => setNewProd({...newProd, category_id: e.target.value})}
                  >
                    <option value="">Select Category</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Initial Stock</label>
                  <input
                    type="number" min="0" required
                    value={newProd.initial_stock}
                    onChange={(e) => setNewProd({...newProd, initial_stock: e.target.value})}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  rows="2"
                  placeholder="Customer-facing description…"
                  value={newProd.description}
                  onChange={(e) => setNewProd({...newProd, description: e.target.value})}
                />
              </div>

              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary-button">
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
