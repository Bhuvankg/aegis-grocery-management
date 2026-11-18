/* Star rating component */
export default function StarRating({ rating, max = 5, size = 16 }) {
  return (
    <span className="star-rating" aria-label={`${rating} out of ${max} stars`}>
      {Array.from({ length: max }, (_, i) => (
        <span
          key={i}
          className={i < Math.round(rating) ? "star filled" : "star"}
          style={{ fontSize: size }}
        >
          ★
        </span>
      ))}
    </span>
  );
}
