import { Link } from "react-router-dom";
import { X, Trash2, ArrowRight, ShoppingBag } from "lucide-react";
import { useCart } from "../context/CartContext";

export default function CartDrawer() {
  const {
    items,
    isOpen,
    closeCart,
    updateQuantity,
    removeFromCart,
    subtotal,
    deliveryFee,
    totalAmount,
  } = useCart();

  if (!isOpen) return null;

  const freeDeliveryDiff = Math.max(0, 500 - subtotal);

  return (
    <div className="cart-drawer-backdrop" onClick={closeCart}>
      <div className="cart-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="cart-drawer-header">
          <div className="cart-drawer-title">
            <ShoppingBag size={20} />
            <h3>Your Shopping Cart ({items.length})</h3>
          </div>
          <button className="cart-close-btn" onClick={closeCart} aria-label="Close cart">
            <X size={20} />
          </button>
        </div>

        {/* Free Delivery Meter */}
        {subtotal > 0 && (
          <div className="free-shipping-banner">
            {freeDeliveryDiff > 0 ? (
              <p>Add <strong>₹{freeDeliveryDiff.toFixed(2)}</strong> more for <strong>FREE delivery</strong>!</p>
            ) : (
              <p className="free-unlocked">🎉 You qualified for <strong>FREE delivery</strong>!</p>
            )}
            <div className="shipping-progress-bar">
              <div
                className="shipping-progress-fill"
                style={{ width: `${Math.min(100, (subtotal / 500) * 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Cart Item List */}
        <div className="cart-items-list">
          {items.length === 0 ? (
            <div className="empty-cart-state">
              <ShoppingBag size={48} className="empty-icon" />
              <p>Your grocery basket is empty.</p>
              <Link to="/products" onClick={closeCart} className="primary-button shop-btn">
                Browse Fresh Groceries
              </Link>
            </div>
          ) : (
            items.map((item) => (
              <div key={item.id} className="cart-item-row">
                <div className="cart-item-info">
                  <h4>{item.name}</h4>
                  <div className="cart-item-price">
                    ₹{item.selling_price.toFixed(2)}
                    {item.unit && <span className="unit"> / {item.unit}</span>}
                  </div>
                </div>

                <div className="cart-item-actions">
                  <div className="qty-control">
                    <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>-</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                  </div>
                  <span className="cart-line-total">
                    ₹{(item.selling_price * item.quantity).toFixed(2)}
                  </span>
                  <button
                    className="cart-delete-btn"
                    onClick={() => removeFromCart(item.id)}
                    title="Remove item"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer with totals */}
        {items.length > 0 && (
          <div className="cart-drawer-footer">
            <div className="cart-summary-line">
              <span>Subtotal</span>
              <span>₹{subtotal.toFixed(2)}</span>
            </div>
            <div className="cart-summary-line">
              <span>Delivery Fee</span>
              <span>{deliveryFee === 0 ? "FREE" : `₹${deliveryFee.toFixed(2)}`}</span>
            </div>
            <div className="cart-summary-line total-line">
              <span>Estimated Total</span>
              <span>₹{totalAmount.toFixed(2)}</span>
            </div>

            <Link
              to="/checkout"
              onClick={closeCart}
              className="primary-button checkout-btn"
            >
              Proceed to Checkout <ArrowRight size={17} />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
