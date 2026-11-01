
"""
Medication Inventory - SQLite Backend

EDUCATIONAL DEMONSTRATION ONLY.

ALL INVENTORY DATA MUST BE FABRICATED.
This application is not intended for actual pharmacy inventory,
medication dispensing, patient care, or clinical decisions.
"""

import calendar
import re
import sqlite3
from datetime import date, datetime
from pathlib import Path


DATABASE = Path(__file__).resolve().with_name("medications.db")


from contextlib import contextmanager

@contextmanager
def connect_db():
    """Open, commit or roll back, and close the SQLite connection."""
    conn = sqlite3.connect(DATABASE, timeout=10)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:
            yield conn
    finally:
        conn.close()


def valid_ndc(value):
    """Require exactly 11 ASCII digits."""
    return (
        isinstance(value, str)
        and len(value) == 11
        and value.isascii()
        and value.isdigit()
    )


def validate_ndc(value):
    return valid_ndc(value)


def validate_date(value):
    """Accept only valid dates formatted YYYY-MM-DD."""
    if not isinstance(value, str):
        return False

    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def months_after(day, months):
    """Advance calendar months, clamping to the final valid day."""
    if not isinstance(day, date):
        raise ValueError("Starting date must be a date.")

    if type(months) is not int:
        raise ValueError("Months must be an integer.")

    index = day.year * 12 + day.month - 1 + months
    year, zero_month = divmod(index, 12)
    month = zero_month + 1

    return date(
        year,
        month,
        min(day.day, calendar.monthrange(year, month)[1])
    )


def create_database():
    """Initialize tables and the combined inventory view."""
    with connect_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                ndc TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                strength TEXT NOT NULL,
                package_size TEXT NOT NULL,
                CHECK(length(ndc) = 11)
            );

            CREATE TABLE IF NOT EXISTS stock_lots (
                id INTEGER PRIMARY KEY,
                ndc TEXT NOT NULL REFERENCES products(ndc),
                lot_number TEXT NOT NULL,
                expiration_date TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0
                    CHECK(quantity >= 0),
                UNIQUE(ndc, lot_number, expiration_date)
            );

            CREATE TABLE IF NOT EXISTS amber_vials (
                id INTEGER PRIMARY KEY,
                ndc TEXT NOT NULL REFERENCES products(ndc),
                source_stock_id INTEGER NOT NULL
                    REFERENCES stock_lots(id),
                lot_number TEXT NOT NULL DEFAULT '00000000'
                    CHECK(lot_number = '00000000'),
                created_date TEXT NOT NULL,
                expiration_date TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity >= 0)
            );

            CREATE TABLE IF NOT EXISTS movements (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                kind TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                ndc TEXT NOT NULL,
                delta INTEGER NOT NULL,
                note TEXT NOT NULL
            );

            CREATE VIEW IF NOT EXISTS inventory_totals AS
            SELECT
                p.ndc,
                p.name,
                p.brand,
                p.strength,
                p.package_size,

                COALESCE(
                    (SELECT SUM(s.quantity)
                     FROM stock_lots s
                     WHERE s.ndc = p.ndc),
                    0
                ) AS stock_units,

                COALESCE(
                    (SELECT SUM(a.quantity)
                     FROM amber_vials a
                     WHERE a.ndc = p.ndc),
                    0
                ) AS vial_units,

                COALESCE(
                    (SELECT SUM(s.quantity)
                     FROM stock_lots s
                     WHERE s.ndc = p.ndc),
                    0
                ) +
                COALESCE(
                    (SELECT SUM(a.quantity)
                     FROM amber_vials a
                     WHERE a.ndc = p.ndc),
                    0
                ) AS total_units

            FROM products p;
        """)


def legacy_status():
    """Count rows in the old medications table, if present."""
    with connect_db() as conn:
        exists = conn.execute(
            """SELECT 1 FROM sqlite_master
               WHERE type = 'table' AND name = 'medications'"""
        ).fetchone()

        if not exists:
            return 0

        return conn.execute(
            "SELECT COUNT(*) FROM medications"
        ).fetchone()[0]


def record(conn, kind, typ, item_id, ndc, delta, note=""):
    """Record a simulated inventory movement."""
    conn.execute(
        """INSERT INTO movements
           (timestamp, kind, item_type, item_id, ndc, delta, note)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            kind,
            typ,
            item_id,
            ndc,
            delta,
            note
        )
    )


def register_product(ndc, name, brand, strength, package_size):
    """Register a demonstration product by NDC."""
    fields = (ndc, name, brand, strength, package_size)

    if not all(isinstance(value, str) for value in fields):
        raise ValueError("All product fields must be text.")

    ndc, name, brand, strength, package_size = (
        value.strip() for value in fields
    )

    if not valid_ndc(ndc):
        raise ValueError("NDC must contain exactly 11 ASCII digits.")

    if not all((name, brand, strength, package_size)):
        raise ValueError("All product fields are required.")

    new_details = (name, brand, strength, package_size)

    with connect_db() as conn:
        existing = conn.execute(
            """SELECT name, brand, strength, package_size
               FROM products WHERE ndc = ?""",
            (ndc,)
        ).fetchone()

        if existing:
            if tuple(x.casefold() for x in existing) != tuple(
                x.casefold() for x in new_details
            ):
                raise ValueError(
                    "NDC already exists with different product details."
                )

            return False

        conn.execute(
            """INSERT INTO products
               (ndc, name, brand, strength, package_size)
               VALUES (?, ?, ?, ?, ?)""",
            (ndc, *new_details)
        )

        return True


def add_stock_lot(ndc, lot, expiration):
    """Add a stock lot with zero initial units."""
    if not isinstance(ndc, str) or not valid_ndc(ndc.strip()):
        raise ValueError("Enter a valid 11-digit NDC.")

    if not isinstance(lot, str):
        raise ValueError("Lot number must be text.")

    ndc = ndc.strip()
    lot = lot.strip()

    if not lot:
        raise ValueError("Lot number cannot be empty.")

    if lot == "00000000":
        raise ValueError(
            "Lot 00000000 is reserved for simulated amber vials."
        )

    if not validate_date(expiration):
        raise ValueError("Expiration must use YYYY-MM-DD.")

    with connect_db() as conn:
        product = conn.execute(
            "SELECT 1 FROM products WHERE ndc = ?",
            (ndc,)
        ).fetchone()

        if not product:
            raise ValueError("Register the product before adding stock.")

        existing = conn.execute(
            """SELECT id FROM stock_lots
               WHERE ndc = ? AND lot_number = ?
               AND expiration_date = ?""",
            (ndc, lot, expiration)
        ).fetchone()

        if existing:
            return existing[0]

        cursor = conn.execute(
            """INSERT INTO stock_lots
               (ndc, lot_number, expiration_date, quantity)
               VALUES (?, ?, ?, 0)""",
            (ndc, lot, expiration)
        )

        return cursor.lastrowid


def adjust_stock(stock_id, change, note="Scanner"):
    """
    Adjust simulated stock quantities.

    Expired stock cannot receive additional units.
    Negative adjustments remain possible for disposal or correction.
    """
    if type(stock_id) is not int or stock_id <= 0:
        raise ValueError("Stock ID must be a positive integer.")

    if type(change) is not int or change == 0:
        raise ValueError("Adjustment must be a nonzero integer.")

    with connect_db() as conn:
        conn.execute("BEGIN IMMEDIATE")

        row = conn.execute(
            """SELECT ndc, quantity, expiration_date
               FROM stock_lots WHERE id = ?""",
            (stock_id,)
        ).fetchone()

        if not row:
            raise ValueError("Stock lot not found.")

        ndc, quantity, expiration = row

        if quantity + change < 0:
            raise ValueError("Insufficient stock units.")

        if change > 0 and expiration < date.today().isoformat():
            raise ValueError("Cannot add units to expired stock.")

        conn.execute(
            """UPDATE stock_lots
               SET quantity = quantity + ?
               WHERE id = ?""",
            (change, stock_id)
        )

        record(
            conn,
            "IN" if change > 0 else "OUT",
            "STOCK",
            stock_id,
            ndc,
            change,
            note
        )

        return quantity + change


def create_amber_vial(stock_id, quantity, created=None):
    """
    Transfer simulated stock units into an amber vial.

    Expiration is the earlier of:
    - Six calendar months from creation.
    - Original stock expiration.

    This is a software demonstration rule, not clinical guidance.
    """
    if type(stock_id) is not int or stock_id <= 0:
        raise ValueError("Source stock ID must be positive.")

    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Transfer quantity must be positive.")

    if created is None:
        created = date.today()

    if type(created) is not date or created != date.today():
        raise ValueError("Creation date must be today.")

    with connect_db() as conn:
        conn.execute("BEGIN IMMEDIATE")

        row = conn.execute(
            """SELECT ndc, quantity, expiration_date
               FROM stock_lots WHERE id = ?""",
            (stock_id,)
        ).fetchone()

        if not row:
            raise ValueError("Source stock lot not found.")

        ndc, available, stock_expiration = row

        if available < quantity:
            raise ValueError(
                f"Only {available} units available in source stock."
            )

        if stock_expiration < created.isoformat():
            raise ValueError("Cannot transfer expired stock.")

        vial_expiration = min(
            months_after(created, 6).isoformat(),
            stock_expiration
        )

        conn.execute(
            """UPDATE stock_lots
               SET quantity = quantity - ?
               WHERE id = ?""",
            (quantity, stock_id)
        )

        cursor = conn.execute(
            """INSERT INTO amber_vials
               (ndc, source_stock_id, created_date,
                expiration_date, quantity)
               VALUES (?, ?, ?, ?, ?)""",
            (
                ndc,
                stock_id,
                created.isoformat(),
                vial_expiration,
                quantity
            )
        )

        vial_id = cursor.lastrowid

        record(
            conn,
            "TRANSFER",
            "STOCK",
            stock_id,
            ndc,
            -quantity,
            f"To amber vial #{vial_id}"
        )

        record(
            conn,
            "TRANSFER",
            "AMBER",
            vial_id,
            ndc,
            quantity,
            f"From stock #{stock_id}"
        )

        return vial_id, vial_expiration


def adjust_vial(vial_id, change):
    """
    Remove units from a simulated amber vial.

    Removal represents a generic inventory reduction, such as
    simulated disposal or correction. It is not dispensing.
    """
    if type(vial_id) is not int or vial_id <= 0:
        raise ValueError("Vial ID must be a positive integer.")

    if type(change) is not int or change >= 0:
        raise ValueError("Vial adjustment must be negative.")

    with connect_db() as conn:
        conn.execute("BEGIN IMMEDIATE")

        row = conn.execute(
            """SELECT ndc, quantity, expiration_date
               FROM amber_vials WHERE id = ?""",
            (vial_id,)
        ).fetchone()

        if not row:
            raise ValueError("Amber vial not found.")

        ndc, quantity, expiration = row

        if quantity + change < 0:
            raise ValueError("Insufficient amber vial units.")

        conn.execute(
            """UPDATE amber_vials
               SET quantity = quantity + ?
               WHERE id = ?""",
            (change, vial_id)
        )

        note = (
            "Simulated expired-inventory removal"
            if expiration < date.today().isoformat()
            else "Simulated inventory removal"
        )

        record(
            conn,
            "OUT",
            "AMBER",
            vial_id,
            ndc,
            change,
            note
        )

        return quantity + change


def parse_positive_id(value, label="Record ID"):
    """Safely convert a short ASCII decimal ID to an integer."""
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[0-9]{1,18}", value)
    ):
        raise ValueError(
            f"{label} must contain 1 to 18 ASCII digits."
        )

    result = int(value)

    if result <= 0:
        raise ValueError(f"{label} must be greater than zero.")

    return result


def search_lots(term):
    """Search by stock lot, NDC, or medication name."""
    if not isinstance(term, str) or len(term) > 120:
        raise ValueError(
            "Search term must be text of at most 120 characters."
        )

    escaped = (
        term.strip()
        .replace("!", "!!")
        .replace("%", "!%")
        .replace("_", "!_")
    )

    pattern = f"%{escaped}%"

    with connect_db() as conn:
        return conn.execute(
            """SELECT
                   s.id, s.ndc, p.name, p.brand, p.strength,
                   s.lot_number, s.expiration_date, s.quantity
               FROM stock_lots s
               JOIN products p ON p.ndc = s.ndc
               WHERE s.lot_number LIKE ? ESCAPE '!'
                  OR s.ndc LIKE ? ESCAPE '!'
                  OR p.name LIKE ? ESCAPE '!'
               ORDER BY p.name, s.expiration_date, s.id""",
            (pattern, pattern, pattern)
        ).fetchall()


def process_scan(raw):
    """
    Process application-specific scanner commands.

    Examples:
        IN:12345678901|LOT123
        OUT:12345678901|LOT123
        IN:STOCK-12
        OUT:STOCK-12
        OUT:VIAL-123

    Each command adjusts one simulated unit.
    """
    if not isinstance(raw, str) or len(raw) > 256:
        raise ValueError(
            "Scanner command must be text of at most 256 characters."
        )

    prefix, separator, payload = raw.strip().partition(":")
    action = prefix.upper()

    if not separator or action not in ("IN", "OUT"):
        raise ValueError(
            "Use IN:NDC|LOT, OUT:NDC|LOT, or OUT:VIAL-123."
        )

    payload = payload.strip()

    if not payload:
        raise ValueError("Scanner command is missing an identifier.")

    if payload.upper().startswith("VIAL-"):
        if action != "OUT":
            raise ValueError(
                "Vials can only receive units through stock transfers."
            )

        vial_id = parse_positive_id(payload[5:], "Vial ID")
        remaining = adjust_vial(vial_id, -1)

        return (
            f"AMBER vial #{vial_id}: "
            f"{remaining} units remain"
        )

    if payload.upper().startswith("STOCK-"):
        stock_id = parse_positive_id(payload[6:], "Stock ID")

        remaining = adjust_stock(
            stock_id,
            1 if action == "IN" else -1
        )

        return (
            f"STOCK #{stock_id}: "
            f"{remaining} units remain"
        )

    ndc, delimiter, lot = payload.partition("|")

    if not valid_ndc(ndc):
        raise ValueError("Invalid 11-digit NDC.")

    if delimiter and (not lot or lot != lot.strip()):
        raise ValueError("Provide a valid lot number.")

    with connect_db() as conn:
        if delimiter:
            rows = conn.execute(
                """SELECT id FROM stock_lots
                   WHERE ndc = ? AND lot_number = ?""",
                (ndc, lot)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id FROM stock_lots WHERE ndc = ?",
                (ndc,)
            ).fetchall()

    if len(rows) != 1:
        raise ValueError(
            "Scan must identify exactly one stock lot. "
            "Use NDC|LOT or STOCK-ID."
        )

    stock_id = rows[0][0]

    remaining = adjust_stock(
        stock_id,
        1 if action == "IN" else -1
    )

    return (
        f"STOCK #{stock_id}: "
        f"{remaining} units remain"
    )


def migrate_legacy_rows(metadata):
    """
    Import rows from the old medications table.

    This is intended for legacy demonstration databases.
    The original table is preserved.

    Metadata format:
        {
            "12345678901": ("10 mg", "30 tablets")
        }
    """
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary.")

    with connect_db() as conn:
        conn.execute("BEGIN IMMEDIATE")

        exists = conn.execute(
            """SELECT 1 FROM sqlite_master
               WHERE type = 'table' AND name = 'medications'"""
        ).fetchone()

        if not exists:
            return 0

        rows = conn.execute(
            """SELECT id, name, brand, ndc, expiration_date,
                      lot_number, quantity
               FROM medications"""
        ).fetchall()

        imported_count = 0
        
        for _, name, brand, ndc, expiration, lot, qty in rows:
            if ndc not in metadata:
                raise ValueError(
                    f"Missing metadata for NDC {ndc}."
                )

            if not valid_ndc(ndc):
                raise ValueError("Invalid legacy NDC.")

            if not validate_date(expiration):
                raise ValueError("Invalid legacy expiration date.")

            if lot == "00000000":
                raise ValueError(
                    "Legacy lot 00000000 requires manual review."
                )

            if type(qty) is not int or qty < 0:
                raise ValueError("Invalid legacy quantity.")

            strength, package_size = metadata[ndc]

            if not all(
                isinstance(x, str) and x.strip()
                for x in (name, brand, strength, package_size)
            ):
                raise ValueError("Incomplete legacy product metadata.")

            proposed = (
                name.strip(),
                brand.strip(),
                strength.strip(),
                package_size.strip()
            )

            existing = conn.execute(
                """SELECT name, brand, strength, package_size
                   FROM products WHERE ndc = ?""",
                (ndc,)
            ).fetchone()

            if existing:
                if tuple(x.casefold() for x in existing) != tuple(
                    x.casefold() for x in proposed
                ):
                    raise ValueError(
                        f"Conflicting product information for {ndc}."
                    )
            else:
                conn.execute(
                    """INSERT INTO products
                       (ndc, name, brand, strength, package_size)
                       VALUES (?, ?, ?, ?, ?)""",
                    (ndc, *proposed)
                )

            
            cursor = conn.execute(
                """INSERT INTO stock_lots
                   (ndc, lot_number, expiration_date, quantity)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(ndc, lot_number, expiration_date)
                   DO NOTHING""",
                (ndc, lot, expiration, qty)
            )
            imported_count += cursor.rowcount

        return imported_count



if __name__ == "__main__":
    create_database()

    print("Medication Inventory database initialized.")
    print("Database location:", DATABASE)
    print("Legacy rows:", legacy_status())
    print("DEMONSTRATION ONLY - ALL DATA MUST BE FABRICATED.")
