import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { ArrowRight, Leaf, ShoppingBag } from "lucide-react";
import HomePage from "./pages/HomePage";
import ProductsPage from "./pages/ProductsPage";
import ProductDetailPage from "./pages/ProductDetailPage";
import AdminLoginPage from "./pages/AdminLoginPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import CheckoutPage from "./pages/CheckoutPage";
import OrderConfirmationPage from "./pages/OrderConfirmationPage";
import CartDrawer from "./components/CartDrawer";
import { CartProvider, useCart } from "./context/CartContext";

function CartNavButton() {
  const { totalItemCount, openCart } = useCart();
  return (
    <button className="topbar-cart-btn" onClick={openCart} aria-label="Open Cart">
      <ShoppingBag size={18} />
      <span>Basket</span>
      {totalItemCount > 0 && <span className="cart-badge">{totalItemCount}</span>}
    </button>
  );
}

export default function App() {
  return (
    <CartProvider>
      <BrowserRouter>
        <div className="site-shell">
          <header className="topbar">
            <Link className="brand" to="/" aria-label="AEGIS AI home">
              <span className="brand-mark"><Leaf size={21} /></span>
              <span>AEGIS<span className="brand-ai"> AI</span></span>
            </Link>
            <nav className="nav-links" aria-label="Main navigation">
              <Link to="/products">Store Catalogue</Link>
              <a href="/#mission">Our mission</a>
              <a href="/#features">Why AEGIS</a>
            </nav>

            <div className="topbar-right">
              <CartNavButton />
              <Link className="admin-link" to="/admin">
                Admin access <ArrowRight size={15} />
              </Link>
            </div>
          </header>

          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/products/:slug" element={<ProductDetailPage />} />
              <Route path="/checkout" element={<CheckoutPage />} />
              <Route path="/order-confirmation/:orderNumber" element={<OrderConfirmationPage />} />
              <Route path="/admin/login" element={<AdminLoginPage />} />
              <Route path="/admin" element={<AdminDashboardPage />} />
            </Routes>
          </main>

          <CartDrawer />

          <footer>
            <span>© {new Date().getFullYear()} AEGIS AI</span>
            <span>Fresh thinking for local grocery.</span>
          </footer>
        </div>
      </BrowserRouter>
    </CartProvider>
  );
}
