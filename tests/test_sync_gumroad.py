import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_gumroad import build_site, transform_products


class GumroadSyncTests(unittest.TestCase):
    def setUp(self):
        self.product = {
            "id": "gumroad-123", "name": "ELDOVANT Visual Edition",
            "description": "<p>Premium <b>visual</b> assets</p><script>alert('x')</script>",
            "custom_summary": "Editorial digital assets", "published": True, "deleted": False,
            "require_shipping": False, "price": 1900, "currency": "eur", "tags": ["Cinematic Assets"],
            "thumbnail_url": "https://public-files.gumroad.com/example.jpg",
            "short_url": "https://eldovant.gumroad.com/l/example",
        }

    def test_includes_public_product_and_maps_fields(self):
        data = transform_products([self.product])
        self.assertEqual(len(data), 1)
        p = data[0]
        self.assertEqual(p["price"], {"amount": 19.0, "currency": "EUR"})
        self.assertEqual(p["checkoutUrl"], "https://eldovant.gumroad.com/l/example")
        self.assertTrue(p["featured"])
        self.assertIn("Premium visual assets", p["description"])
        self.assertNotIn("alert", p["description"])

    def test_draft_deleted_archived_unlisted_physical_excluded(self):
        records = []
        for flag in ["published", "deleted", "archived", "is_unlisted", "require_shipping"]:
            clone = dict(self.product)
            clone["id"] = flag
            clone[flag] = False if flag == "published" else True
            records.append(clone)
        self.assertEqual(transform_products(records), [])

    def test_only_tagged_optional(self):
        self.assertEqual(transform_products([self.product], required_tag="eldovant-shop"), [])
        with_tag = dict(self.product, tags=["eldovant-shop", "Sound Design"])
        self.assertEqual(transform_products([with_tag], required_tag="eldovant-shop")[0]["category"], "Sound Design")

    def test_skip_bad_url_and_excluded_id(self):
        unsafe = dict(self.product, short_url="javascript:alert(1)")
        self.assertEqual(transform_products([unsafe]), [])
        self.assertEqual(transform_products([self.product], excluded_ids={"gumroad-123"}), [])

    def test_build_only_public_fields(self):
        base = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "site"
            build_site(base, dest, transform_products([self.product]))
            self.assertTrue((dest / "index.html").is_file())
            self.assertFalse((dest / "CNAME").exists())
            source = (dest / "eldovant-data.js").read_text(encoding="utf-8")
            self.assertIn('window.ELDOVANT_DATA = ', source)
            self.assertIn('ELDOVANT Visual Edition', source)
            self.assertIn('eldovant.gumroad.com/l/example', source)
            self.assertNotIn('access_token', source)
            self.assertNotIn('alert', source)


if __name__ == "__main__":
    unittest.main()
