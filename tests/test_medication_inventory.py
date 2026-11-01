
"""
Automated tests for Medication Inventory.

EDUCATIONAL DEMONSTRATION ONLY.
All medication inventory records used in these tests are fabricated.

Run from the project root:

    python -m unittest discover -s tests -v

These tests use a temporary SQLite database and do not modify
the application's regular medications.db file.
"""

import sqlite3
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import medication_inventory as inventory


class MedicationInventoryTests(unittest.TestCase):
    """Test database operations using isolated, fabricated records."""

    NDC = "12345678901"
    NAME = "Demo Medication"
    BRAND = "Demo Brand"
    STRENGTH = "10 mg"
    PACKAGE_SIZE = "30 tablets"
    LOT = "DEMO-LOT-001"

    def setUp(self):
        """Create a new temporary database before each test."""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        database_path = (
            Path(self.temp_directory.name) / "test_medications.db"
        )

        self.database_patch = patch.object(
            inventory,
            "DATABASE",
            database_path
        )
        self.database_patch.start()
        self.addCleanup(self.database_patch.stop)

        inventory.create_database()

        inventory.register_product(
            self.NDC,
            self.NAME,
            self.BRAND,
            self.STRENGTH,
            self.PACKAGE_SIZE
        )

        self.expiration = (
            date.today() + timedelta(days=365)
        ).isoformat()

        self.stock_id = inventory.add_stock_lot(
            self.NDC,
            self.LOT,
            self.expiration
        )

    def get_stock_quantity(self):
        """Return the current quantity for the test stock lot."""
        with inventory.connect_db() as conn:
            row = conn.execute(
                "SELECT quantity FROM stock_lots WHERE id = ?",
                (self.stock_id,)
            ).fetchone()

        return row[0]

    def get_totals(self):
        """Return stock, vial, and combined inventory totals."""
        with inventory.connect_db() as conn:
            return conn.execute(
                """SELECT stock_units, vial_units, total_units
                   FROM inventory_totals WHERE ndc = ?""",
                (self.NDC,)
            ).fetchone()

    def test_database_tables_exist(self):
        """Verify the expected database tables and view exist."""
        with inventory.connect_db() as conn:
            objects = {
                (row[0], row[1])
                for row in conn.execute(
                    """SELECT type, name
                       FROM sqlite_master
                       WHERE type IN ('table', 'view')"""
                ).fetchall()
            }

        for table in (
            "products",
            "stock_lots",
            "amber_vials",
            "movements"
        ):
            self.assertIn(("table", table), objects)

        self.assertIn(
            ("view", "inventory_totals"),
            objects
        )

    def test_register_product(self):
        """Verify a new product is registered correctly."""
        new_ndc = "98765432109"

        result = inventory.register_product(
            new_ndc,
            "Demo Medication Two",
            "Demo Brand Two",
            "20 mg",
            "60 tablets"
        )

        self.assertTrue(result)

        with inventory.connect_db() as conn:
            product = conn.execute(
                "SELECT name FROM products WHERE ndc = ?",
                (new_ndc,)
            ).fetchone()

        self.assertEqual(
            product[0],
            "Demo Medication Two"
        )

    def test_duplicate_product(self):
        """Registering identical product details should be idempotent."""
        result = inventory.register_product(
            self.NDC,
            self.NAME,
            self.BRAND,
            self.STRENGTH,
            self.PACKAGE_SIZE
        )

        self.assertFalse(result)

        with inventory.connect_db() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM products WHERE ndc = ?",
                (self.NDC,)
            ).fetchone()[0]

        self.assertEqual(count, 1)

    def test_conflicting_product_details(self):
        """An existing NDC must not accept conflicting product details."""
        with self.assertRaises(ValueError):
            inventory.register_product(
                self.NDC,
                "Different Demo Medication",
                self.BRAND,
                self.STRENGTH,
                self.PACKAGE_SIZE
            )

    def test_invalid_ndc(self):
        """Reject invalid or incorrectly formatted NDC values."""
        invalid_values = (
            "",
            "123",
            "1234567890",
            "123456789012",
            "12345ABCDE1",
            "12345-67890"
        )

        for value in invalid_values:
            with self.subTest(ndc=value):
                self.assertFalse(
                    inventory.valid_ndc(value)
                )

        self.assertTrue(
            inventory.valid_ndc(self.NDC)
        )

    def test_add_stock_lot(self):
        """New stock lots begin with zero units."""
        self.assertGreater(self.stock_id, 0)
        self.assertEqual(
            self.get_stock_quantity(),
            0
        )

    def test_duplicate_stock_lot(self):
        """Adding the same lot again returns the existing stock ID."""
        duplicate_id = inventory.add_stock_lot(
            self.NDC,
            self.LOT,
            self.expiration
        )

        self.assertEqual(
            duplicate_id,
            self.stock_id
        )

    def test_invalid_expiration_date(self):
        """Reject invalid expiration dates."""
        with self.assertRaises(ValueError):
            inventory.add_stock_lot(
                self.NDC,
                "INVALID-DATE-LOT",
                "2026-99-99"
            )

    def test_stock_in_scan(self):
        """An IN scanner command adds one simulated unit."""
        message = inventory.process_scan(
            f"IN:{self.NDC}|{self.LOT}"
        )

        self.assertEqual(
            self.get_stock_quantity(),
            1
        )
        self.assertIn("1 units remain", message)

    def test_stock_out_scan(self):
        """An OUT scanner command removes one simulated unit."""
        inventory.adjust_stock(self.stock_id, 5)

        inventory.process_scan(
            f"OUT:{self.NDC}|{self.LOT}"
        )

        self.assertEqual(
            self.get_stock_quantity(),
            4
        )

    def test_stock_id_scan(self):
        """Scanner commands can reference a stock record by ID."""
        inventory.process_scan(
            f"IN:STOCK-{self.stock_id}"
        )

        self.assertEqual(
            self.get_stock_quantity(),
            1
        )

    def test_invalid_scanner_commands(self):
        """Reject malformed scanner commands without changing inventory."""
        invalid_commands = (
            "",
            "INVALID",
            "ADD:12345678901",
            "OUT:VIAL-ABC",
            "IN:STOCK-",
            "OUT:123",
            "IN:VIAL-123",
            "OUT:STOCK-0"
        )

        before = self.get_stock_quantity()

        for command in invalid_commands:
            with self.subTest(command=command):
                with self.assertRaises(ValueError):
                    inventory.process_scan(command)

        self.assertEqual(
            self.get_stock_quantity(),
            before
        )

    def test_insufficient_stock(self):
        """Inventory quantities cannot become negative."""
        with self.assertRaises(ValueError):
            inventory.adjust_stock(
                self.stock_id,
                -1
            )

        self.assertEqual(
            self.get_stock_quantity(),
            0
        )

    def test_create_amber_vial(self):
        """Transferring stock into a vial preserves total units."""
        inventory.adjust_stock(
            self.stock_id,
            20
        )

        before = self.get_totals()

        vial_id, expiration = inventory.create_amber_vial(
            self.stock_id,
            8
        )

        after = self.get_totals()

        self.assertGreater(vial_id, 0)
        self.assertEqual(after[0], 12)
        self.assertEqual(after[1], 8)
        self.assertEqual(after[2], before[2])
        self.assertTrue(
            inventory.validate_date(expiration)
        )

    def test_transfer_more_than_available(self):
        """A vial transfer cannot exceed the source quantity."""
        inventory.adjust_stock(
            self.stock_id,
            3
        )

        with self.assertRaises(ValueError):
            inventory.create_amber_vial(
                self.stock_id,
                10
            )

        self.assertEqual(
            self.get_totals(),
            (3, 0, 3)
        )

    def test_amber_vial_scanner(self):
        """Vial OUT scans remove one simulated unit."""
        inventory.adjust_stock(
            self.stock_id,
            10
        )

        vial_id, _ = inventory.create_amber_vial(
            self.stock_id,
            4
        )

        message = inventory.process_scan(
            f"OUT:VIAL-{vial_id}"
        )

        self.assertIn(
            "3 units remain",
            message
        )

        self.assertEqual(
            self.get_totals(),
            (6, 3, 9)
        )

    def test_month_end_expiration(self):
        """Calendar-month calculations handle month-end dates."""
        result = inventory.months_after(
            date(2026, 8, 31),
            6
        )

        self.assertEqual(
            result,
            date(2027, 2, 28)
        )

    def test_vial_expiration_not_after_stock(self):
        """A vial must not expire later than its source stock."""
        inventory.adjust_stock(
            self.stock_id,
            10
        )

        vial_id, vial_expiration = inventory.create_amber_vial(
            self.stock_id,
            5
        )

        self.assertGreater(vial_id, 0)
        self.assertLessEqual(
            vial_expiration,
            self.expiration
        )

    def test_search_by_lot_number(self):
        """Lot-number searches return matching stock records."""
        rows = inventory.search_lots(
            self.LOT
        )

        self.assertEqual(
            len(rows),
            1
        )
        self.assertEqual(
            rows[0][0],
            self.stock_id
        )

    def test_search_by_medication_name(self):
        """Stock records can be found by medication name."""
        rows = inventory.search_lots(
            "Demo Medication"
        )

        self.assertEqual(
            len(rows),
            1
        )

    def test_transaction_history(self):
        """Stock changes must be recorded in the movements table."""
        inventory.adjust_stock(
            self.stock_id,
            5
        )

        inventory.adjust_stock(
            self.stock_id,
            -2
        )

        with inventory.connect_db() as conn:
            rows = conn.execute(
                """SELECT kind, delta
                   FROM movements
                   ORDER BY id"""
            ).fetchall()

        self.assertEqual(
            rows,
            [("IN", 5), ("OUT", -2)]
        )

    def test_expired_stock_rejects_additions(self):
        """Expired stock cannot receive additional simulated units."""
        expired_date = (
            date.today() - timedelta(days=1)
        ).isoformat()

        expired_id = inventory.add_stock_lot(
            self.NDC,
            "EXPIRED-DEMO-LOT",
            expired_date
        )

        with self.assertRaises(ValueError):
            inventory.adjust_stock(
                expired_id,
                1
            )

    def test_invalid_vial_quantity(self):
        """Vial transfers require positive whole-number quantities."""
        inventory.adjust_stock(
            self.stock_id,
            10
        )

        for quantity in (0, -1, 2.5, True):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    inventory.create_amber_vial(
                        self.stock_id,
                        quantity
                    )

    def test_positive_id_validation(self):
        """IDs must contain only valid positive ASCII decimal digits."""
        self.assertEqual(
            inventory.parse_positive_id("123"),
            123
        )

        for invalid in (
            "",
            "0",
            "-1",
            "ABC",
            "1.5",
            "１２３",
            "1234567890123456789"
        ):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    inventory.parse_positive_id(invalid)

    
    def test_expired_stock_cannot_be_transferred(self):
        expired = (date.today() - timedelta(days=1)).isoformat()
        stock_id = inventory.add_stock_lot(
            self.NDC, "OLD-DEMO-LOT", expired
        )

        with self.assertRaises(ValueError):
            inventory.create_amber_vial(stock_id, 1)

    def test_failed_transfer_preserves_inventory(self):
        inventory.adjust_stock(self.stock_id, 3)

        with self.assertRaises(ValueError):
            inventory.create_amber_vial(self.stock_id, 4)

        self.assertEqual(self.get_totals(), (3, 0, 3))

    def test_migration_is_repeatable(self):
        with inventory.connect_db() as conn:
            conn.execute("""CREATE TABLE medications (
                id INTEGER PRIMARY KEY,
                name TEXT, brand TEXT, ndc TEXT,
                expiration_date TEXT, lot_number TEXT,
                quantity INTEGER
            )""")
            conn.execute(
                """INSERT INTO medications
                   (name, brand, ndc, expiration_date,
                    lot_number, quantity)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (self.NAME, self.BRAND, self.NDC,
                 self.expiration, "LEGACY-DEMO-LOT", 7)
            )

        metadata = {
            self.NDC: (self.STRENGTH, self.PACKAGE_SIZE)
        }

        self.assertEqual(
            inventory.migrate_legacy_rows(metadata), 1
        )
        self.assertEqual(
            inventory.migrate_legacy_rows(metadata), 0
        )

    def test_migration_rolls_back_on_invalid_row(self):
        with inventory.connect_db() as conn:
            conn.execute("""CREATE TABLE medications (
                id INTEGER PRIMARY KEY,
                name TEXT, brand TEXT, ndc TEXT,
                expiration_date TEXT, lot_number TEXT,
                quantity INTEGER
            )""")
            conn.executemany(
                """INSERT INTO medications
                   (name, brand, ndc, expiration_date,
                    lot_number, quantity)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (self.NAME, self.BRAND, self.NDC,
                     self.expiration, "LEGACY-GOOD", 5),
                    (self.NAME, self.BRAND, self.NDC,
                     "invalid-date", "LEGACY-BAD", 2),
                ]
            )

        with self.assertRaises(ValueError):
            inventory.migrate_legacy_rows({
                self.NDC: (
                    self.STRENGTH, self.PACKAGE_SIZE
                )
            })

        with inventory.connect_db() as conn:
            count = conn.execute(
                """SELECT COUNT(*) FROM stock_lots
                   WHERE lot_number LIKE 'LEGACY-%'"""
            ).fetchone()[0]

        self.assertEqual(count, 0)

if __name__ == "__main__":
    unittest.main()
