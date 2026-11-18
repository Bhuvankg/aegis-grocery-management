import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  ArrowLeft, ShieldCheck, Truck, CreditCard, CheckCircle2,
  AlertCircle, Sparkles, AlertTriangle
} from "lucide-react";
import { useCart } from "../context/CartContext";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { items, subtotal, deliveryFee, totalAmount, clearCart } = useCart();

  const [form, setForm] = useState({
    customer_name: "",
    customer_phone: "",
    customer_email: "",
    delivery_address: "",
    payment_method: "simulated_online", // default or "cash_on_delivery"
  });

  // Simulation test option for evaluators
  const [simulationOutcome, setSimulationOutcome] = useState("success");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (items.length === 0) {
    return (
      <div className="checkout-page empty-checkout">
        <h2>Your cart is empty</h2>
        <p>Add some fresh groceries before checking out.</p>
        <Link to="/products" className="primary-button">
          Browse Store
        </Link>
      </div>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // 1. Create order on server
      const orderPayload = {
        customer_name: form.customer_name.trim(),
        customer_phone: form.customer_phone.trim(),
        customer_email: form.customer_email.trim() || null,
        delivery_address: form.delivery_address.trim(),
        payment_method: form.payment_method,
        items: items.map((i) => ({
          product_id: i.id,
          quantity: i.quantity,
        })),
      };

      const res = await fetch(`${API_BASE_URL}/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(orderPayload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Order submission failed. Please try again.");
      }

      const order = await res.json();

      // 2. If simulated online payment selected, call simulation endpoint
      if (form.payment_method === "simulated_online") {
        const payRes = await fetch(`${API_BASE_URL}/payments/simulate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            order_number: order.order_number,
            outcome: simulationOutcome,
          }),
        });

        if (!payRes.ok) {
          const payErr = await payRes.json().catch(() => ({}));
          throw new Error(
            payErr.detail || "Simulated payment failed as requested for testing."
          );
        }
      }

      clearCart();
      navigate(`/order-confirmation/${order.order_number}`);
    } catch (err) {
      setError(err.message || "Could not complete order. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout-page">
      <div className="checkout-header">
        <Link to="/products" className="back-link">
          <ArrowLeft size={16} /> Continue Shopping
        </Link>
        <h1>Secure Checkout</h1>
        <p className="checkout-subtitle">
          <ShieldCheck size={16} /> Server-revalidated pricing & instant stock reservation
        </p>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      <div className="checkout-grid">
        {/* Left: Customer & Delivery Details */}
        <form onSubmit={handleSubmit} className="checkout-form">
          <section className="form-card">
            <h3>1. Delivery Information</h3>
            <div className="form-group">
              <label>Full Name *</label>
              <input
                type="text"
                required
                placeholder="e.g. Ramesh Kumar"
                value={form.customer_name}
                onChange={(e) => setForm({ ...form, customer_name: e.target.value })}
              />
            </div>

            <div className="form-row-2">
              <div className="form-group">
                <label>Phone Number *</label>
                <input
                  type="tel"
                  required
                  placeholder="e.g. 9876543210"
                  value={form.customer_phone}
                  onChange={(e) => setForm({ ...form, customer_phone: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Email (for order updates)</label>
                <input
                  type="email"
                  placeholder="name@example.com"
                  value={form.customer_email}
                  onChange={(e) => setForm({ ...form, customer_email: e.target.value })}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Delivery Address *</label>
              <textarea
                required
                rows="3"
                placeholder="Apartment/Flat, Street name, Landmark, City, PIN code"
                value={form.delivery_address}
                onChange={(e) => setForm({ ...form, delivery_address: e.target.value })}
              />
            </div>
          </section>

          <section className="form-card">
            <h3>2. Payment Method</h3>
            <div className="payment-options">
              {/* Option A: Simulated Online Payment */}
              <label
                className={`payment-radio-option ${
                  form.payment_method === "simulated_online" ? "active" : ""
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  value="simulated_online"
                  checked={form.payment_method === "simulated_online"}
                  onChange={(e) => setForm({ ...form, payment_method: e.target.value })}
                />
                <div className="payment-option-text">
                  <div className="payment-title">
                    <CreditCard size={18} /> Instant Online Payment (Simulated Demo)
                  </div>
                  <p className="payment-desc">
                    One-click mock payment simulation for demo evaluators.
                  </p>
                </div>
              </label>

              {/* Simulation Sandbox Box */}
              {form.payment_method === "simulated_online" && (
                <div className="simulation-disclosure-box">
                  <div className="simulation-badge">
                    <Sparkles size={14} /> DEMO PAYMENT SIMULATION
                  </div>
                  <p className="simulation-explainer">
                    In compliance with security rules, <strong>no card numbers or CVVs</strong> are ever collected or stored.
                    No real money will be transferred.
                  </p>
                  <div className="simulation-controls">
                    <label className="sim-choice">
                      <input
                        type="radio"
                        name="simOutcome"
                        value="success"
                        checked={simulationOutcome === "success"}
                        onChange={() => setSimulationOutcome("success")}
                      />
                      <span>✓ Simulate Approved (Success)</span>
                    </label>
                    <label className="sim-choice">
                      <input
                        type="radio"
                        name="simOutcome"
                        value="fail"
                        checked={simulationOutcome === "fail"}
                        onChange={() => setSimulationOutcome("fail")}
                      />
                      <span>✗ Simulate Declined (Failure)</span>
                    </label>
                  </div>
                </div>
              )}

              {/* Option B: Cash on Delivery */}
              <label
                className={`payment-radio-option ${
                  form.payment_method === "cash_on_delivery" ? "active" : ""
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  value="cash_on_delivery"
                  checked={form.payment_method === "cash_on_delivery"}
                  onChange={(e) => setForm({ ...form, payment_method: e.target.value })}
                />
                <div className="payment-option-text">
                  <div className="payment-title">
                    <Truck size={18} /> Cash on Delivery (COD)
                  </div>
                  <p className="payment-desc">Pay cash or UPI upon delivery at your doorstep.</p>
                </div>
              </label>
            </div>
          </section>

          <button type="submit" className="primary-button place-order-btn" disabled={loading}>
            {loading
              ? "Processing Order & Reserving Stock…"
              : `Place Order (₹${totalAmount.toFixed(2)})`}
          </button>
        </form>

        {/* Right: Order Summary */}
        <aside className="order-summary-sidebar">
          <div className="form-card">
            <h3>Order Summary ({items.length} items)</h3>
            <div className="summary-items-list">
              {items.map((i) => (
                <div key={i.id} className="summary-item-line">
                  <div>
                    <strong>{i.name}</strong>
                    <div className="item-meta">
                      Qty: {i.quantity} {i.unit ? `· ${i.unit}` : ""}
                    </div>
                  </div>
                  <span>₹{(i.selling_price * i.quantity).toFixed(2)}</span>
                </div>
              ))}
            </div>

            <div className="summary-divider" />

            <div className="summary-calc-row">
              <span>Subtotal</span>
              <span>₹{subtotal.toFixed(2)}</span>
            </div>
            <div className="summary-calc-row">
              <span>Delivery Fee</span>
              <span>{deliveryFee === 0 ? "FREE" : `₹${deliveryFee.toFixed(2)}`}</span>
            </div>
            <div className="summary-calc-row total">
              <span>Total Payable</span>
              <span>₹{totalAmount.toFixed(2)}</span>
            </div>

            <div className="assurance-box">
              <CheckCircle2 size={16} />
              <span>Real-time inventory deduction & order reference guarantee</span>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
