import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { useCart } from "../context/CartContext";

const EMOJI_MAP = {
  "fruits-vegetables": "🥦",
  "dairy-eggs": "🥛",
  "bakery": "🍞",
  "pantry": "🌾",
  "beverages": "☕",
  "snacks": "🥜",
  "meat-seafood": "🐟",
  "frozen-foods": "❄️",
};

export default function ProductCard({ product }) {
  const { addToCart } = useCart();
  const inStock = product.inventory?.quantity > 0;
  const lowStock =
    product.inventory?.quantity > 0 &&
    product.inventory.quantity <= (product.inventory.reorder_level ?? 10);
  const emoji = product.category?.slug
    ? EMOJI_MAP[product.category.slug]
    : "🛒";

  const handleAdd = (e) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(product, 1);
  };

  return (
    <div className="product-card">
      <Link
        to={`/products/${product.slug}`}
        className="product-card-link"
        aria-label={product.name}
      >
        <div className="product-card-image">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} loading="lazy" />
          ) : (
            <span className="product-emoji">{emoji}</span>
          )}
          {!inStock && <span className="badge badge-out">Out of stock</span>}
          {lowStock && <span className="badge badge-low">Low stock</span>}
        </div>

        <div className="product-card-body">
          {product.category && (
            <span className="product-category-tag">
              {product.category.name}
            </span>
          )}
          <h3 className="product-name">{product.name}</h3>
          <div className="product-price-row">
            <span className="product-price">
              ₹{Number(product.selling_price).toFixed(2)}
            </span>
            {product.unit && (
              <span className="product-unit">/ {product.unit}</span>
            )}
          </div>
        </div>
      </Link>

      <div className="product-card-footer">
        <button
          className={`quick-add-btn ${!inStock ? "disabled" : ""}`}
          onClick={handleAdd}
          disabled={!inStock}
          title={inStock ? "Add to Cart" : "Out of Stock"}
        >
          <Plus size={15} /> {inStock ? "Add to cart" : "Sold out"}
        </button>
      </div>
    </div>
  );
}
