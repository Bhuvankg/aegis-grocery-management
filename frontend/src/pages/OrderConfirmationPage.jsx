import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  CheckCircle, MapPin, Phone, ArrowLeft, Copy, Check,
  CreditCard, Truck, ShieldAlert
} from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export default function OrderConfirmationPage() {
  const { orderNumber } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/orders/${orderNumber}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setOrder(data))
      .catch(() => setOrder(null))
      .finally(() => setLoading(false));
  }, [orderNumber]);

  const copyOrderRef = () => {
    navigator.clipboard.writeText(orderNumber);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="confirmation-page">
        <div className="confirmation-skeleton">Loading your order receipt…</div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="confirmation-page not-found">
        <h2>Order Not Found</h2>
        <p>We could not locate reference <code>{orderNumber}</code>.</p>
        <Link to="/products" className="primary-button">
          Browse Store
        </Link>
      </div>
    );
  }

  const isOnlineSim = order.payment_method === "simulated_online";
  const hasPaid = order.payment?.status === "success" || isOnlineSim;

  return (
    <div className="confirmation-page">
      <div className="confirmation-card">
        <div className="confirmation-success-icon">
          <CheckCircle size={48} />
        </div>

        <h1>Thank You for Your Order!</h1>
        <p className="confirmation-subtitle">
          Your order has been received and confirmed. Stock has been reserved.
        </p>

        {/* Order Reference Box */}
        <div className="order-ref-box">
          <div className="ref-label">Order Reference</div>
          <div className="ref-value-row">
            <span className="order-number-text">{order.order_number}</span>
            <button className="copy-btn" onClick={copyOrderRef} title="Copy Order Reference">
              {copied ? <Check size={16} color="#1c5d38" /> : <Copy size={16} />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
          <span className="order-status-badge">{order.status.toUpperCase()}</span>
        </div>

        {/* Payment Summary Box */}
        <div className={`payment-receipt-box ${isOnlineSim ? "sim-paid" : "cod"}`}>
          <div className="payment-receipt-header">
            {isOnlineSim ? <CreditCard size={18} /> : <Truck size={18} />}
            <strong>
              {isOnlineSim ? "Paid via Simulated Online Payment" : "Payment Method: Cash on Delivery"}
            </strong>
          </div>
          {isOnlineSim ? (
            <div className="simulation-receipt-details">
              {order.payment?.transaction_reference && (
                <div className="sim-ref-line">
                  Simulated Txn ID: <code>{order.payment.transaction_reference}</code>
                </div>
              )}
              <div className="simulation-disclaimer-pill">
                <ShieldAlert size={13} />
                <span>DEMO SIMULATION: No actual money was deducted or transferred.</span>
              </div>
            </div>
          ) : (
            <p className="cod-receipt-note">
              Please pay ₹{Number(order.total_amount).toFixed(2)} in cash or UPI to the delivery executive.
            </p>
          )}
        </div>

        {/* Delivery Details */}
        <div className="confirmation-details-grid">
          <div className="detail-item">
            <div className="detail-item-title"><MapPin size={16} /> Delivery Address</div>
            <p>{order.delivery_address}</p>
          </div>
          <div className="detail-item">
            <div className="detail-item-title"><Phone size={16} /> Contact Details</div>
            <p><strong>{order.customer_name}</strong> · {order.customer_phone}</p>
            {order.customer_email && <p className="email-sub">{order.customer_email}</p>}
          </div>
        </div>

        {/* Itemized Table */}
        <div className="receipt-items-container">
          <h3>Order Details</h3>
          <table className="receipt-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {order.items.map((item) => (
                <tr key={item.id}>
                  <td><strong>{item.product_name_snapshot}</strong></td>
                  <td>{item.quantity}</td>
                  <td>₹{Number(item.unit_price).toFixed(2)}</td>
                  <td>₹{Number(item.line_total).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan="3">Subtotal</td>
                <td>₹{Number(order.subtotal).toFixed(2)}</td>
              </tr>
              <tr>
                <td colSpan="3">Delivery Fee</td>
                <td>{Number(order.delivery_fee) === 0 ? "FREE" : `₹${Number(order.delivery_fee).toFixed(2)}`}</td>
              </tr>
              <tr className="receipt-total-row">
                <td colSpan="3">{hasPaid ? "Total Paid (Simulated)" : "Total Due on Delivery"}</td>
                <td>₹{Number(order.total_amount).toFixed(2)}</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <div className="confirmation-actions">
          <Link to="/products" className="primary-button">
            <ArrowLeft size={16} /> Continue Shopping
          </Link>
        </div>
      </div>
    </div>
  );
}
