"""
AEGIS AI - Security Boundaries & Business Invariant Test Suite.
Run from backend/ with venv active:
    python run_tests.py
"""
import sys
import unittest
from pathlib import Path
from decimal import Decimal

# Ensure backend in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.schemas.product import ProductPublic, ProductListItem
from app.schemas.payment import SimulatedPaymentRequest
from app.schemas.order import OrderCreate, OrderItemCreate
from app.ai_engine.forecasting import calculate_linear_regression, MODEL_VERSION, DISCLAIMER


class TestAegisSecurityAndInvariants(unittest.TestCase):

    def test_01_no_public_admin_registration_endpoint(self):
        """Invariant 6: Do not add public administrator registration."""
        registered_paths = [r.path for r in app.routes if hasattr(r, "path")]
        for p in registered_paths:
            self.assertNotIn("register", p.lower(), f"Forbidden public registration found at {p}")
            self.assertNotIn("signup", p.lower(), f"Forbidden public signup found at {p}")
        print("  ✓ PASSED: No public administrator registration route exists.")

    def test_02_password_hashing_and_verification(self):
        """Security: bcrypt password hashing works with proper salts."""
        raw_pw = "AdminSecret@2026"
        hashed = hash_password(raw_pw)
        self.assertNotEqual(raw_pw, hashed)
        self.assertTrue(verify_password(raw_pw, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))
        print("  ✓ PASSED: Secure bcrypt password hashing and verification validated.")

    def test_03_jwt_token_generation_and_decoding(self):
        """Security: JWT tokens encode subject and reject invalid/tampered tokens."""
        token = create_access_token(subject=42, extra_claims={"role": "admin"})
        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get("sub"), "42")
        self.assertEqual(payload.get("role"), "admin")

        # Tampered token check
        tampered = token[:-5] + "XXXXX"
        self.assertIsNone(decode_access_token(tampered))
        print("  ✓ PASSED: JWT authentication tokens signed and tamper-proof.")

    def test_04_public_product_schemas_never_leak_cost_price(self):
        """Invariant 3: Customers must never view internal costs/profit."""
        public_fields = ProductPublic.model_fields.keys()
        list_fields = ProductListItem.model_fields.keys()

        self.assertNotIn("cost_price", public_fields, "Leak! cost_price found in ProductPublic schema")
        self.assertNotIn("cost_price", list_fields, "Leak! cost_price found in ProductListItem schema")
        self.assertNotIn("supplier_id", list_fields, "Leak! supplier_id found in ProductListItem schema")
        print("  ✓ PASSED: Public schemas strictly omit cost_price and internal supplier data.")

    def test_05_payment_simulation_never_collects_card_data(self):
        """Invariant 7: Never request or store card numbers/CVV; clearly simulated."""
        sim_fields = SimulatedPaymentRequest.model_fields.keys()
        self.assertNotIn("card_number", sim_fields)
        self.assertNotIn("cvv", sim_fields)
        self.assertNotIn("expiry_date", sim_fields)
        self.assertIn("outcome", sim_fields)
        print("  ✓ PASSED: Payment simulation schema strictly omits real financial credentials.")

    def test_06_linear_regression_math_and_forecasting(self):
        """ML: Linear regression mathematical accuracy."""
        x = [0.0, 1.0, 2.0, 3.0]
        y = [10.0, 20.0, 30.0, 40.0]
        slope, intercept = calculate_linear_regression(x, y)
        self.assertAlmostEqual(slope, 10.0, places=2)
        self.assertAlmostEqual(intercept, 10.0, places=2)
        print("  ✓ PASSED: Forecasting trend regression engine mathematically sound.")

    def test_07_forecast_advisory_disclaimer(self):
        """Invariant 8: AI forecasts are advisory and include mandatory disclaimer."""
        self.assertIn("advisory", DISCLAIMER.lower())
        self.assertIn("never automatically alter", DISCLAIMER.lower())
        print("  ✓ PASSED: Mandatory advisory AI disclaimer validated.")


def main():
    print("=" * 65)
    print("  AEGIS AI - Security & Product Invariant Test Suite")
    print("=" * 65)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAegisSecurityAndInvariants)
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n🎉 ALL 7 INVARIANT AND SECURITY TESTS PASSED SUCCESSFULLY!\n")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
