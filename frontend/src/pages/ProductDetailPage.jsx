import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Package, Info, Calendar, Star, ShoppingBag, Check } from "lucide-react";
import { fetchProductBySlug, fetchProductReviews, submitReview } from "../services/api";
import StarRating from "../components/StarRating";
import { useCart } from "../context/CartContext";

export default function ProductDetailPage() {
  const { slug } = useParams();
  const navigate = useNavigate();

  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  // Review form state
  const [rating, setRating] = useState(5);
  const [body, setBody] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [addedNotice, setAddedNotice] = useState(false);
  const { addToCart } = useCart();

  useEffect(() => {
    setLoading(true);
    fetchProductBySlug(slug)
      .then((data) => {
        if (!data) { setNotFound(true); return; }
        setProduct(data);
        return fetchProductReviews(data.id);
      })
      .then((r) => r && setReviews(r))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [slug]);

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError("");
    try {
      await submitReview(product.id, { rating, body });
      setSubmitted(true);
      setBody("");
      setRating(5);
    } catch {
      setSubmitError("Could not submit review. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
    <div className="detail-page">
      <div className="detail-skeleton" />
    </div>
  );

  if (notFound) return (
    <div className="detail-page not-found">
      <span>🔍</span>
      <h2>Product not found</h2>
      <Link to="/products" className="back-link">← Back to catalogue</Link>
    </div>
  );

  const inStock = product.inventory?.quantity > 0;
  const qty = product.inventory?.quantity ?? 0;

  return (
    <div className="detail-page">
      <div className="detail-breadcrumb">
        <Link to="/products" className="back-link"><ArrowLeft size={15} /> Back to products</Link>
        {product.category && (
          <> <span className="breadcrumb-sep">/</span>
            <span className="breadcrumb-cat">{product.category.name}</span>
          </>
        )}
      </div>

      <div className="detail-layout">
        {/* Image / emoji panel */}
        <div className="detail-image-panel">
          {product.image_url
            ? <img src={product.image_url} alt={product.name} className="detail-img" />
            : <span className="detail-emoji">🛒</span>
          }
          <div className={`stock-badge ${inStock ? "in-stock" : "out-stock"}`}>
            <Package size={13} />
            {inStock ? `${qty} in stock` : "Out of stock"}
          </div>
        </div>

        {/* Info panel */}
        <div className="detail-info">
          {product.category && (
            <span className="product-category-tag">{product.category.name}</span>
          )}
          <h1 className="detail-name">{product.name}</h1>

          {reviews && reviews.total > 0 && (
            <div className="detail-rating-row">
              <StarRating rating={reviews.average_rating} size={18} />
              <span className="rating-count">({reviews.total} review{reviews.total !== 1 ? "s" : ""})</span>
            </div>
          )}

          <div className="detail-price-row">
            <span className="detail-price">₹{Number(product.selling_price).toFixed(2)}</span>
            {product.unit && <span className="detail-unit">/ {product.unit}</span>}
          </div>

          {product.description && (
            <p className="detail-description">{product.description}</p>
          )}

          {/* Quality notes — clearly labelled as store-entered */}
          {product.quality_notes && (
            <div className="detail-info-box">
              <div className="info-box-title"><Info size={13} /> Quality information (store-entered)</div>
              <p>{product.quality_notes}</p>
            </div>
          )}

          {product.expiry_info && (
            <div className="detail-info-box">
              <div className="info-box-title"><Calendar size={13} /> Storage & freshness</div>
              <p>{product.expiry_info}</p>
            </div>
          )}

          <button
            className={`add-to-cart-btn${!inStock ? " disabled" : ""}`}
            disabled={!inStock}
            onClick={() => {
              addToCart(product, 1);
              setAddedNotice(true);
              setTimeout(() => setAddedNotice(false), 2000);
            }}
          >
            {addedNotice ? "✓ Added to basket!" : inStock ? "Add to cart" : "Out of stock"}
          </button>
        </div>
      </div>

      {/* Reviews section */}
      <section className="reviews-section">
        <h2 className="reviews-title">
          <Star size={18} /> Customer Reviews
          {reviews && reviews.total > 0 && (
            <span className="reviews-avg"> · {reviews.average_rating?.toFixed(1)} / 5</span>
          )}
        </h2>

        {!reviews || reviews.total === 0 ? (
          <p className="no-reviews">No reviews yet — be the first!</p>
        ) : (
          <div className="reviews-list">
            {reviews.items.map((r) => (
              <article key={r.id} className="review-card">
                <div className="review-header">
                  <StarRating rating={r.rating} size={14} />
                  <span className="review-date">
                    {new Date(r.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
                  </span>
                </div>
                {r.body && <p className="review-body">{r.body}</p>}
              </article>
            ))}
          </div>
        )}

        {/* Submit review form */}
        <div className="review-form-wrap">
          <h3>Write a review</h3>
          {submitted
            ? <div className="review-submitted">✅ Thank you! Your review is pending approval.</div>
            : (
              <form className="review-form" onSubmit={handleReviewSubmit}>
                <div className="rating-picker">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <button
                      key={s}
                      type="button"
                      className={`rating-star${s <= rating ? " selected" : ""}`}
                      onClick={() => setRating(s)}
                      aria-label={`${s} star${s > 1 ? "s" : ""}`}
                    >★</button>
                  ))}
                  <span className="rating-label">{rating} / 5</span>
                </div>
                <textarea
                  className="review-textarea"
                  placeholder="Share your experience (optional)…"
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  maxLength={2000}
                  rows={4}
                />
                {submitError && <p className="submit-error">{submitError}</p>}
                <button type="submit" className="submit-review-btn" disabled={submitting}>
                  {submitting ? "Submitting…" : "Submit review"}
                </button>
              </form>
            )
          }
        </div>
      </section>
    </div>
  );
}
