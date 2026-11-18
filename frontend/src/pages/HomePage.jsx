import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Leaf, ShieldCheck, ShoppingBasket, Sparkles, TrendingUp } from "lucide-react";
import { checkApiHealth, fetchProducts } from "../services/api";
import ProductCard from "../components/ProductCard";

const highlights = [
  { icon: ShoppingBasket, title: "Thoughtful shopping", text: "A clean customer experience for discovering everyday essentials." },
  { icon: TrendingUp, title: "Smarter store decisions", text: "Inventory and sales intelligence designed for independent grocers." },
  { icon: ShieldCheck, title: "Admin-only controls", text: "Private management tools protected behind server-side authorization." },
];

export default function HomePage() {
  const [apiStatus, setApiStatus] = useState("Checking API…");
  const [featured, setFeatured] = useState([]);

  useEffect(() => {
    checkApiHealth()
      .then(() => setApiStatus("API connected"))
      .catch(() => setApiStatus("API not reachable – start the backend"));

    fetchProducts({ pageSize: 4 })
      .then((data) => setFeatured(data.items))
      .catch(() => {});
  }, []);

  return (
    <div>
      {/* Hero */}
      <section className="hero" id="mission">
        <div className="hero-copy">
          <div className="eyebrow"><Sparkles size={15} /> INTELLIGENCE FOR EVERYDAY GROCERY</div>
          <h1>Fresh choices.<br /><span>Smarter stores.</span></h1>
          <p className="hero-text">
            AEGIS AI brings simple grocery shopping and intelligent store management
            together — helping local stores make better decisions with their data.
          </p>
          <div className="hero-actions">
            <Link className="primary-button" to="/products">
              Shop now <ArrowRight size={17} />
            </Link>
            <span className="trust-note"><ShieldCheck size={16} /> Built for independent grocers</span>
          </div>
          <div className="status-line"><span className="status-dot" /> {apiStatus}</div>
        </div>
        <div className="hero-art" aria-label="Fresh grocery illustration">
          <div className="art-orbit orbit-one" />
          <div className="art-orbit orbit-two" />
          <div className="produce-card">
            <div className="produce-emoji">🥑</div>
            <div className="produce-caption">Fresh, local, simple</div>
            <div className="produce-pills"><span>Quality</span><span>Value</span><span>Care</span></div>
          </div>
          <div className="floating-tag tag-top">✦ Better stock decisions</div>
          <div className="floating-tag tag-bottom">↗ Made for local stores</div>
        </div>
      </section>

      {/* Featured products strip */}
      {featured.length > 0 && (
        <section className="featured-section">
          <div className="section-heading">
            <span className="eyebrow">FRESH TODAY</span>
            <h2>Featured products</h2>
          </div>
          <div className="product-grid product-grid-4">
            {featured.map((p) => <ProductCard key={p.id} product={p} />)}
          </div>
          <div className="featured-cta">
            <Link to="/products" className="primary-button">
              View all products <ArrowRight size={16} />
            </Link>
          </div>
        </section>
      )}

      {/* Features */}
      <section className="feature-section" id="features">
        <div className="section-heading">
          <span className="eyebrow">ONE PLATFORM, TWO EXPERIENCES</span>
          <h2>Good for customers.<br /><span>Powerful for store owners.</span></h2>
        </div>
        <div className="feature-grid">
          {highlights.map(({ icon: Icon, title, text }) => (
            <article className="feature-card" key={title}>
              <div className="feature-icon"><Icon size={22} /></div>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
