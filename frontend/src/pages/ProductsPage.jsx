import { useEffect, useState, useCallback } from "react";
import { Search, X } from "lucide-react";
import { fetchCategories, fetchProducts } from "../services/api";
import ProductCard from "../components/ProductCard";

export default function ProductsPage() {
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 12;

  const [selectedCategory, setSelectedCategory] = useState(null);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load categories once
  useEffect(() => {
    fetchCategories()
      .then(setCategories)
      .catch(() => setCategories([]));
  }, []);

  // Load products when filters change
  const loadProducts = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchProducts({ page, pageSize, categoryId: selectedCategory, search })
      .then((data) => {
        setProducts(data.items);
        setTotal(data.total);
      })
      .catch(() => setError("Failed to load products. Is the backend running?"))
      .finally(() => setLoading(false));
  }, [page, selectedCategory, search]);

  useEffect(() => { loadProducts(); }, [loadProducts]);

  const handleSearch = (e) => {
    e.preventDefault();
    setSearch(searchInput.trim());
    setPage(1);
  };

  const clearSearch = () => {
    setSearchInput("");
    setSearch("");
    setPage(1);
  };

  const selectCategory = (id) => {
    setSelectedCategory(id === selectedCategory ? null : id);
    setPage(1);
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="products-page">
      {/* Search bar */}
      <div className="search-bar-wrap">
        <form className="search-bar" onSubmit={handleSearch}>
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search products…"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            aria-label="Search products"
          />
          {searchInput && (
            <button type="button" className="search-clear" onClick={clearSearch} aria-label="Clear search">
              <X size={14} />
            </button>
          )}
          <button type="submit" className="search-submit">Search</button>
        </form>
      </div>

      <div className="products-layout">
        {/* Category sidebar */}
        <aside className="category-sidebar">
          <h2 className="sidebar-title">Categories</h2>
          <ul className="category-list">
            <li>
              <button
                className={`category-btn${!selectedCategory ? " active" : ""}`}
                onClick={() => selectCategory(null)}
              >
                All products
                <span className="cat-count">{total}</span>
              </button>
            </li>
            {categories.map((cat) => (
              <li key={cat.id}>
                <button
                  className={`category-btn${selectedCategory === cat.id ? " active" : ""}`}
                  onClick={() => selectCategory(cat.id)}
                >
                  {cat.name}
                </button>
              </li>
            ))}
          </ul>
        </aside>

        {/* Product grid */}
        <main className="products-main">
          <div className="products-header">
            <p className="products-count">
              {loading ? "Loading…" : `${total} product${total !== 1 ? "s" : ""}${search ? ` for "${search}"` : ""}`}
            </p>
          </div>

          {error && <div className="error-banner">{error}</div>}

          {!loading && products.length === 0 && !error && (
            <div className="empty-state">
              <span>🔍</span>
              <p>No products found{search ? ` for "${search}"` : ""}.</p>
              {(search || selectedCategory) && (
                <button className="clear-filters-btn" onClick={() => { clearSearch(); setSelectedCategory(null); }}>
                  Clear filters
                </button>
              )}
            </div>
          )}

          <div className="product-grid">
            {loading
              ? Array.from({ length: 8 }).map((_, i) => <div key={i} className="product-card-skeleton" />)
              : products.map((p) => <ProductCard key={p.id} product={p} />)
            }
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button disabled={page === 1} onClick={() => setPage(page - 1)} className="page-btn">← Prev</button>
              <span className="page-info">Page {page} of {totalPages}</span>
              <button disabled={page === totalPages} onClick={() => setPage(page + 1)} className="page-btn">Next →</button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
