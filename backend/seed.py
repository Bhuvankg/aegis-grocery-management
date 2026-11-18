"""
Seed script — populates the AEGIS AI database with sample grocery data.
Run from the backend directory:
    python seed.py

Safe to re-run: existing records are skipped (upsert by slug/sku).
"""
import sys
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

# Ensure app package is importable when run from backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.review import Review

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"name": "Fruits & Vegetables", "slug": "fruits-vegetables", "description": "Fresh seasonal fruits and vegetables"},
    {"name": "Dairy & Eggs",         "slug": "dairy-eggs",        "description": "Milk, cheese, butter, and eggs"},
    {"name": "Bakery",               "slug": "bakery",            "description": "Breads, cakes, and baked goods"},
    {"name": "Pantry",               "slug": "pantry",            "description": "Rice, lentils, oils, spices, and dry goods"},
    {"name": "Beverages",            "slug": "beverages",         "description": "Water, juices, tea, and coffee"},
    {"name": "Snacks",               "slug": "snacks",            "description": "Biscuits, nuts, and packaged snacks"},
    {"name": "Meat & Seafood",       "slug": "meat-seafood",      "description": "Fresh and frozen meat and fish"},
    {"name": "Frozen Foods",         "slug": "frozen-foods",      "description": "Frozen vegetables, meals, and ice cream"},
]

SUPPLIERS = [
    {"name": "FreshFarm Co.",       "phone": "9876543210", "email": "supply@freshfarm.in",    "address": "Bengaluru, Karnataka"},
    {"name": "Daily Dairy Ltd.",    "phone": "9123456780", "email": "orders@dailydairy.in",   "address": "Pune, Maharashtra"},
    {"name": "Golden Bakery House", "phone": "9988776655", "email": "bulk@goldenbakery.in",   "address": "Chennai, Tamil Nadu"},
    {"name": "Pantry Plus",         "phone": "9871234560", "email": "trade@pantryplus.in",    "address": "Hyderabad, Telangana"},
    {"name": "SeaBreeze Fisheries", "phone": "9001234567", "email": "fresh@seabreeze.in",     "address": "Kochi, Kerala"},
]

# (name, slug, sku, description, selling_price, cost_price, unit, image_url,
#  quality_notes, expiry_info, category_slug, supplier_name, qty, reorder_level)
PRODUCTS = [
    # --- Fruits & Vegetables ---
    ("Alphonso Mangoes",   "alphonso-mangoes",   "FV-001", "Sweet Alphonso mangoes from Ratnagiri",
     149.00, 95.00,  "kg",  None,
     "Store-sourced; graded by size and colour. Not independently certified.",
     "Best consumed within 3-4 days of purchase.",
     "fruits-vegetables", "FreshFarm Co.", 80, 15),

    ("Baby Spinach",       "baby-spinach",       "FV-002", "Tender baby spinach leaves, pre-washed",
     49.00,  28.00,  "250g", None,
     "Packed fresh daily at the farm. No pesticide residue testing is performed by us.",
     "Use within 2 days. Store refrigerated.",
     "fruits-vegetables", "FreshFarm Co.", 60, 10),

    ("Cherry Tomatoes",    "cherry-tomatoes",    "FV-003", "Bright red cherry tomatoes",
     79.00,  45.00,  "500g", None,
     "Sourced from local greenhouse farms.",
     "Best before 5 days. Keep refrigerated.",
     "fruits-vegetables", "FreshFarm Co.", 50, 10),

    ("Avocado",            "avocado",            "FV-004", "Creamy Hass avocados",
     89.00,  55.00,  "pcs",  None,
     "Imported; ripeness may vary.",
     "Ripen at room temperature; refrigerate once ripe.",
     "fruits-vegetables", "FreshFarm Co.", 40, 8),

    # --- Dairy & Eggs ---
    ("Full Cream Milk",    "full-cream-milk",    "DE-001", "Pasteurised full cream milk, 1 litre",
     68.00,  52.00,  "1L",   None,
     "Pasteurised and homogenised. Quality as per supplier declaration.",
     "Use by date printed on pack. Keep refrigerated.",
     "dairy-eggs", "Daily Dairy Ltd.", 120, 20),

    ("Paneer",             "paneer",             "DE-002", "Fresh cottage cheese, 200g",
     85.00,  60.00,  "200g", None,
     "Made fresh daily. Store-declared shelf life.",
     "Consume within 2 days. Keep refrigerated.",
     "dairy-eggs", "Daily Dairy Ltd.", 70, 15),

    ("Free-Range Eggs",    "free-range-eggs",    "DE-003", "Farm eggs, tray of 12",
     95.00,  72.00,  "12 pcs", None,
     "Supplier declares free-range rearing. Not independently verified by us.",
     "Best before 2 weeks. Refrigerate.",
     "dairy-eggs", "Daily Dairy Ltd.", 90, 20),

    ("Greek Yogurt",       "greek-yogurt",       "DE-004", "Thick and creamy Greek-style yogurt, 400g",
     120.00, 88.00,  "400g", None,
     "Contains live active cultures per supplier label.",
     "Best before date on pack.",
     "dairy-eggs", "Daily Dairy Ltd.", 55, 10),

    # --- Bakery ---
    ("Sourdough Loaf",     "sourdough-loaf",     "BK-001", "Artisan sourdough baked in-house",
     120.00, 70.00,  "loaf", None,
     "Baked fresh each morning. No preservatives per baker's declaration.",
     "Best consumed within 2 days.",
     "bakery", "Golden Bakery House", 30, 5),

    ("Whole Wheat Bread",  "whole-wheat-bread",  "BK-002", "Soft whole wheat sandwich bread, 400g",
     55.00,  35.00,  "400g", None,
     "Contains whole wheat flour. Nutritional info on pack.",
     "Best before date printed on packaging.",
     "bakery", "Golden Bakery House", 45, 10),

    ("Butter Croissants",  "butter-croissants",  "BK-003", "Flaky all-butter croissants, pack of 4",
     130.00, 85.00,  "4 pcs", None,
     "Contains butter and wheat. Allergen info on pack.",
     "Best consumed the day of purchase.",
     "bakery", "Golden Bakery House", 25, 5),

    # --- Pantry ---
    ("Basmati Rice",       "basmati-rice",       "PT-001", "Aged long-grain basmati rice, 5kg",
     549.00, 390.00, "5kg",  None,
     "Sourced from Punjab. Aged 2 years as per supplier.",
     "Store in a cool, dry place. No expiry if stored properly.",
     "pantry", "Pantry Plus", 100, 20),

    ("Toor Dal",           "toor-dal",           "PT-002", "Split pigeon peas, 1kg",
     145.00, 100.00, "1kg",  None,
     "Machine cleaned and sorted.",
     "Best within 12 months. Store airtight.",
     "pantry", "Pantry Plus", 80, 15),

    ("Cold-Pressed Coconut Oil", "cold-pressed-coconut-oil", "PT-003",
     "Virgin cold-pressed coconut oil, 500ml",
     299.00, 210.00, "500ml", None,
     "Supplier declares cold-pressed extraction. Not independently certified.",
     "Use within 18 months. Store away from sunlight.",
     "pantry", "Pantry Plus", 60, 10),

    ("Turmeric Powder",    "turmeric-powder",    "PT-004", "Pure turmeric powder, 100g",
     45.00,  28.00,  "100g", None,
     "No artificial colour per supplier declaration.",
     "Best before 12 months from manufacturing. Store airtight.",
     "pantry", "Pantry Plus", 90, 15),

    # --- Beverages ---
    ("Green Tea",          "green-tea",          "BV-001", "Premium whole-leaf green tea, 100g",
     250.00, 170.00, "100g", None,
     "Sourced from Darjeeling estates per supplier.",
     "Best before 18 months. Store in airtight tin.",
     "beverages", "Pantry Plus", 50, 10),

    ("Cold Brew Coffee",   "cold-brew-coffee",   "BV-002", "Ready-to-drink cold brew coffee, 300ml",
     99.00,  65.00,  "300ml", None,
     "Contains caffeine. Ingredient list on bottle.",
     "Refrigerate; use within 7 days of opening.",
     "beverages", "Pantry Plus", 40, 8),

    ("Coconut Water",      "coconut-water",      "BV-003", "Natural tender coconut water, 200ml",
     40.00,  25.00,  "200ml", None,
     "Minimally processed; no added sugar per label.",
     "Best before date on pack. Refrigerate after opening.",
     "beverages", "FreshFarm Co.", 100, 20),

    # --- Snacks ---
    ("Mixed Nuts",         "mixed-nuts",         "SN-001", "Roasted mixed nuts: almonds, cashews, walnuts, 200g",
     299.00, 210.00, "200g", None,
     "Lightly salted. Contains tree nuts — allergen info on pack.",
     "Best before 6 months. Store cool and dry.",
     "snacks", "Pantry Plus", 60, 10),

    ("Rice Crackers",      "rice-crackers",      "SN-002", "Light and crispy rice crackers, 150g",
     79.00,  48.00,  "150g", None,
     "Contains rice and sesame. Gluten-free per supplier.",
     "Best before date on pack.",
     "snacks", "Pantry Plus", 70, 12),

    # --- Meat & Seafood ---
    ("Chicken Breast",     "chicken-breast",     "MS-001", "Boneless skinless chicken breast, 500g",
     249.00, 175.00, "500g", None,
     "Chilled, not frozen. Store-received same day.",
     "Use within 2 days. Keep refrigerated at or below 4°C.",
     "meat-seafood", "SeaBreeze Fisheries", 40, 10),

    ("Atlantic Salmon",    "atlantic-salmon",    "MS-002", "Fresh Atlantic salmon fillet, 300g",
     549.00, 390.00, "300g", None,
     "Chilled; store-received daily. Source: supplier declaration.",
     "Use within 1-2 days. Refrigerate immediately.",
     "meat-seafood", "SeaBreeze Fisheries", 20, 5),

    # --- Frozen Foods ---
    ("Frozen Mixed Vegetables", "frozen-mixed-veg", "FF-001",
     "Peas, carrots, corn, beans — IQF frozen, 500g",
     89.00,  58.00,  "500g", None,
     "Individually quick-frozen. No preservatives per pack label.",
     "Best before 12 months. Keep frozen at -18°C.",
     "frozen-foods", "FreshFarm Co.", 60, 12),

    ("Vanilla Ice Cream",  "vanilla-ice-cream",  "FF-002", "Creamy vanilla ice cream, 500ml",
     199.00, 135.00, "500ml", None,
     "Contains milk and eggs. See pack for allergen info.",
     "Best before 3 months. Keep frozen.",
     "frozen-foods", "Daily Dairy Ltd.", 35, 8),
]

# (product_slug, rating, body, is_approved)
REVIEWS = [
    ("alphonso-mangoes",    5, "Absolutely the best mangoes I've ever had! Sweet and aromatic.", True),
    ("alphonso-mangoes",    4, "Very fresh, arrived in good condition. Will order again.", True),
    ("baby-spinach",        5, "So fresh and clean. Perfect for smoothies and salads.", True),
    ("full-cream-milk",     4, "Good quality milk, kids love it.", True),
    ("paneer",              5, "Fresh and soft, makes excellent dishes.", True),
    ("sourdough-loaf",      5, "Best sourdough in town! Perfect crust and chewy inside.", True),
    ("sourdough-loaf",      4, "Really good bread. Delivery packaging could be better.", True),
    ("basmati-rice",        5, "Excellent aroma and long grains. Very authentic.", True),
    ("mixed-nuts",          4, "Great mix and good quantity. Almonds were especially fresh.", True),
    ("chicken-breast",      5, "Very fresh, no smell. Great quality.", True),
    ("atlantic-salmon",     5, "Incredibly fresh! Cooked beautifully.", True),
    ("green-tea",           4, "Delicate flavour, clearly good quality leaves.", True),
    ("cold-brew-coffee",    5, "Smooth and not too bitter. My morning favourite now.", True),
    ("greek-yogurt",        4, "Thick and creamy, just right.", True),
    ("free-range-eggs",     3, "Eggs were fine but one broke in transit.", True),
    ("vanilla-ice-cream",   5, "Classic and creamy. Family loved it!", True),
    ("frozen-mixed-veg",    4, "Handy to have in the freezer. Good quality.", True),
    # Pending reviews (not yet approved — should NOT show in public API)
    ("cherry-tomatoes",     2, "A few were squashed. Disappointed.", False),
    ("butter-croissants",   1, "Stale. Clearly not same-day.", False),
]


# ---------------------------------------------------------------------------
# Seeder
# ---------------------------------------------------------------------------

def seed():
    db = SessionLocal()
    try:
        # 1. Categories
        print("\n── Categories ──")
        cat_map: dict[str, Category] = {}
        for c in CATEGORIES:
            existing = db.query(Category).filter_by(slug=c["slug"]).first()
            if existing:
                cat_map[c["slug"]] = existing
                print(f"  skip  {c['name']}")
            else:
                obj = Category(**c, is_active=True)
                db.add(obj)
                db.flush()
                cat_map[c["slug"]] = obj
                print(f"  added {c['name']}")

        # 2. Suppliers
        print("\n── Suppliers ──")
        sup_map: dict[str, Supplier] = {}
        for s in SUPPLIERS:
            existing = db.query(Supplier).filter_by(name=s["name"]).first()
            if existing:
                sup_map[s["name"]] = existing
                print(f"  skip  {s['name']}")
            else:
                obj = Supplier(**s)
                db.add(obj)
                db.flush()
                sup_map[s["name"]] = obj
                print(f"  added {s['name']}")

        # 3. Products + Inventory
        print("\n── Products ──")
        prod_map: dict[str, Product] = {}
        for row in PRODUCTS:
            (name, slug, sku, desc, sell, cost, unit, img,
             qual, exp, cat_slug, sup_name, qty, reorder) = row

            existing = db.query(Product).filter_by(sku=sku).first()
            if existing:
                prod_map[slug] = existing
                print(f"  skip  {name}")
                continue

            product = Product(
                name=name,
                slug=slug,
                sku=sku,
                description=desc,
                selling_price=Decimal(str(sell)),
                cost_price=Decimal(str(cost)),
                unit=unit,
                image_url=img,
                quality_notes=qual,
                expiry_info=exp,
                category_id=cat_map[cat_slug].id,
                supplier_id=sup_map[sup_name].id,
                is_active=True,
            )
            db.add(product)
            db.flush()
            prod_map[slug] = product

            # Inventory row
            inventory = Inventory(
                product_id=product.id,
                quantity=qty,
                reorder_level=reorder,
            )
            db.add(inventory)
            print(f"  added {name}  (qty={qty})")

        # 4. Reviews
        print("\n── Reviews ──")
        for (prod_slug, rating, body, approved) in REVIEWS:
            product = prod_map.get(prod_slug)
            if not product:
                print(f"  skip  review for unknown slug: {prod_slug}")
                continue

            exists = (
                db.query(Review)
                .filter_by(product_id=product.id, body=body)
                .first()
            )
            if exists:
                print(f"  skip  review for {prod_slug}")
                continue

            review = Review(
                product_id=product.id,
                rating=rating,
                body=body,
                is_approved=approved,
            )
            db.add(review)
            status = "approved" if approved else "pending"
            print(f"  added [{status}] review for {prod_slug} ({rating}★)")

        db.commit()
        print("\n✅  Seed complete!\n")

    except Exception as e:
        db.rollback()
        print(f"\n❌  Seed failed: {type(e).__name__}: {e}\n")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
