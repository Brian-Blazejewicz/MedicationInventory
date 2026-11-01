
"""SQLite backend for the medication inventory application.

Manage medication products, stock lots, amber vials, and inventory
movements. Quantities represent individual medication units.

This application is intended for educational and testing purposes,
not for clinical medication dispensing.
"""

import calendar
import sqlite3
from datetime import date, datetime
from pathlib import Path


# Store the SQLite database alongside this Python module.
DATABASE = Path(__file__).resolve().with_name('medications.db')


def connect_db():
    """Open a SQLite connection with foreign-key enforcement enabled.

    Returns:
        sqlite3.Connection: A connection to the inventory database.
    """
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def valid_ndc(value):
    """Check whether an NDC contains exactly 11 ASCII digits.

    Args:
        value (str): The medication's National Drug Code.

    Returns:
        bool: True if the NDC has the required format.
    """
    return len(value) == 11 and value.isascii() and value.isdigit()


def validate_ndc(value):
    """Provide an alternate entry point for NDC validation.

    Args:
        value (str): The NDC to validate.

    Returns:
        bool: The result of the NDC format check.
    """
    return valid_ndc(value)


def validate_date(value):
    """Validate a date string in ISO YYYY-MM-DD format.

    Args:
        value (str): The date string to check.

    Returns:
        bool: True if the value represents a valid ISO date.
    """
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def months_after(day, months):
    """Calculate a date a specified number of calendar months later.

    If the target month has fewer days than the starting month,
    use the final valid day of the target month.

    Args:
        day (date): The starting date.
        months (int): Number of months to advance.

    Returns:
        date: The calculated calendar date.
    """
    index = day.year * 12 + day.month - 1 + months
    year, zero_month = divmod(index, 12)
    month = zero_month + 1

    return date(
        year,
        month,
        min(day.day, calendar.monthrange(year, month)[1])
    )


def create_database():
    """Create the inventory tables and combined-quantity view.

    Existing tables are preserved. The database contains separate
    records for products, stock lots, amber vials, and movements.

    The inventory_totals view combines stock and amber vial
    quantities for each registered NDC.
    """
    with connect_db() as db:
        db.execute(
            '''CREATE TABLE IF NOT EXISTS products (
                ndc TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                strength TEXT NOT NULL,
                package_size TEXT NOT NULL,
                CHECK(length(ndc)=11)
            )'''
        )

        db.execute(
            '''CREATE TABLE IF NOT EXISTS stock_lots (
                id INTEGER PRIMARY KEY,
                ndc TEXT NOT NULL REFERENCES products(ndc),
                lot_number TEXT NOT NULL,
                expiration_date TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0
                    CHECK(quantity>=0),
                UNIQUE(ndc,lot_number,expiration_date)
            )'''
        )

        db.execute(
            '''CREATE TABLE IF NOT EXISTS amber_vials (
                id INTEGER PRIMARY KEY,
                ndc TEXT NOT NULL REFERENCES products(ndc),
                source_stock_id INTEGER NOT NULL
                    REFERENCES stock_lots(id),
                lot_number TEXT NOT NULL DEFAULT '00000000'
                    CHECK(lot_number='00000000'),
                created_date TEXT NOT NULL,
                expiration_date TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity>=0)
            )'''
        )

        db.execute(
            '''CREATE TABLE IF NOT EXISTS movements (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                kind TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                ndc TEXT NOT NULL,
                delta INTEGER NOT NULL,
                note TEXT NOT NULL
            )'''
        )

        # Combine stock and amber vial quantities without
        # duplicating the physical inventory records.
        db.execute(
            '''CREATE VIEW IF NOT EXISTS inventory_totals AS
                SELECT
                    p.ndc,
                    p.name,
                    p.brand,
                    p.strength,
                    p.package_size,

                    COALESCE(
                        (SELECT SUM(quantity)
                         FROM stock_lots s
                         WHERE s.ndc=p.ndc), 0
                    ) AS stock_units,

                    COALESCE(
                        (SELECT SUM(quantity)
                         FROM amber_vials a
                         WHERE a.ndc=p.ndc), 0
                    ) AS vial_units,

                    COALESCE(
                        (SELECT SUM(quantity)
                         FROM stock_lots s
                         WHERE s.ndc=p.ndc), 0
                    ) +

                    COALESCE(
                        (SELECT SUM(quantity)
                         FROM amber_vials a
                         WHERE a.ndc=p.ndc), 0
                    ) AS total_units

                FROM products p'''
        )


def legacy_status():
    """Count records remaining in the preserved legacy table.

    This function checks whether the old medications table exists.
    It does not determine whether those records have already been
    migrated into the new inventory tables.

    Returns:
        int: Number of legacy medication rows, or zero if the
        legacy table does not exist.
    """
    with connect_db() as db:
        present = db.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type='table' AND name='medications'"
        ).fetchone()

        if not present:
            return 0

        return db.execute(
            'SELECT COUNT(*) FROM medications'
        ).fetchone()[0]


def record(db, kind, typ, item_id, ndc, delta, note=''):
    """Insert an inventory movement into the transaction history.

    Args:
        db (sqlite3.Connection): Active database connection.
        kind (str): Movement category, such as IN, OUT, or TRANSFER.
        typ (str): Inventory item type, such as STOCK or AMBER.
        item_id (int): Identifier of the affected stock lot or vial.
        ndc (str): NDC associated with the movement.
        delta (int): Signed quantity change.
        note (str): Optional description of the movement.
    """
    db.execute(
        '''INSERT INTO movements
           (timestamp,kind,item_type,item_id,ndc,delta,note)
           VALUES(?,?,?,?,?,?,?)''',
        (
            datetime.now().astimezone().isoformat(
                timespec='seconds'
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
    """Register a medication product using its unique NDC.

    Reject incomplete product details and conflicting information
    for an NDC that is already registered.

    Args:
        ndc (str): Eleven-digit medication identifier.
        name (str): Medication name.
        brand (str): Brand name.
        strength (str): Medication strength.
        package_size (str): Package size description.

    Returns:
        bool: True if a new product was inserted; False if an
        identical product was already registered.

    Raises:
        ValueError: If required fields are invalid or an existing
        NDC has conflicting product details.
    """
    ndc, name, brand, strength, package_size = (
        value.strip()
        for value in (
            ndc, name, brand, strength, package_size
        )
    )

    if not valid_ndc(ndc) or not all(
        (name, brand, strength, package_size)
    ):
        raise ValueError(
            'NDC must be 11 digits; all product fields are required.'
        )

    with connect_db() as db:
        old = db.execute(
            '''SELECT name,brand,strength,package_size
               FROM products WHERE ndc=?''',
            (ndc,)
        ).fetchone()

        new = (name, brand, strength, package_size)

        if old:
            if tuple(x.casefold() for x in old) != tuple(
                x.casefold() for x in new
            ):
                raise ValueError(
                    'NDC conflict: existing medication, brand, '
                    'strength or package size differs.'
                )

            return False

        db.execute(
            'INSERT INTO products VALUES(?,?,?,?,?)',
            (ndc, *new)
        )

        return True


def add_stock_lot(ndc, lot, expiration):
    """Register a stock lot with an initial quantity of zero.

    A stock lot must reference an existing product. The reserved
    lot number 00000000 cannot be used for stock lots.

    If the same NDC, lot number, and expiration date already exist,
    the duplicate insertion is ignored.

    Args:
        ndc (str): NDC of the registered product.
        lot (str): Stock lot number.
        expiration (str): Expiration date in YYYY-MM-DD format.

    Raises:
        ValueError: If the lot information is invalid or the
        product has not been registered.
    """
    if (
        not lot.strip()
        or lot.strip() == '00000000'
        or not validate_date(expiration)
    ):
        raise ValueError(
            'Enter a valid stock lot (not 00000000) '
            'and YYYY-MM-DD expiration.'
        )

    with connect_db() as db:
        if not db.execute(
            'SELECT 1 FROM products WHERE ndc=?',
            (ndc,)
        ).fetchone():
            raise ValueError('Register the product NDC first.')

        db.execute(
            '''INSERT OR IGNORE INTO stock_lots
               (ndc,lot_number,expiration_date)
               VALUES(?,?,?)''',
            (ndc, lot.strip(), expiration)
        )


def adjust_stock(stock_id, change, note='Scanner'):
    """Increase or decrease the quantity of an existing stock lot.

    Record the quantity adjustment as an inventory movement.
    Prevent negative inventory and receiving units into expired
    stock lots.

    Args:
        stock_id (int): Identifier of the stock lot.
        change (int): Signed quantity adjustment.
        note (str): Description recorded with the movement.

    Returns:
        int: Updated quantity of the stock lot.

    Raises:
        ValueError: If the stock lot does not exist, inventory
        would become negative, or expired stock is being received.
    """
    with connect_db() as db:
        # Acquire a write transaction before reading the quantity.
        db.execute('BEGIN IMMEDIATE')

        row = db.execute(
            '''SELECT ndc,quantity,expiration_date
               FROM stock_lots WHERE id=?''',
            (stock_id,)
        ).fetchone()

        if not row:
            raise ValueError('Stock lot not found.')

        ndc, qty, expiration = row

        if qty + change < 0:
            raise ValueError('Insufficient stock.')

        if change > 0 and expiration < date.today().isoformat():
            raise ValueError('Cannot receive expired stock.')

        db.execute(
            '''UPDATE stock_lots
               SET quantity=quantity+?
               WHERE id=?''',
            (change, stock_id)
        )

        record(
            db,
            'IN' if change > 0 else 'OUT',
            'STOCK',
            stock_id,
            ndc,
            change,
            note
        )

        return qty + change


def create_amber_vial(stock_id, quantity, created=None):
    """Transfer units from a stock lot into a new amber vial.

    The vial receives lot number 00000000. Its expiration date
    is six calendar months after creation, or the source stock
    expiration date if that occurs sooner.

    The transfer decreases source stock and increases vial stock
    by the same quantity, preserving combined inventory totals.

    Args:
        stock_id (int): Identifier of the source stock lot.
        quantity (int): Number of individual units to transfer.
        created (date, optional): Creation date; must equal today.

    Returns:
        tuple: New vial ID and expiration date string.

    Raises:
        ValueError: If the quantity is invalid, the creation date
        is not today, the source stock is missing or expired, or
        there are insufficient units.
    """
    if type(quantity) is not int or quantity <= 0:
        raise ValueError(
            'Vial quantity must be a positive whole number.'
        )

    created = created or date.today()

    if created != date.today():
        raise ValueError(
            'Creation date must be today; '
            'historical backdating is disabled.'
        )

    with connect_db() as db:
        db.execute('BEGIN IMMEDIATE')

        row = db.execute(
            '''SELECT ndc,quantity,expiration_date
               FROM stock_lots WHERE id=?''',
            (stock_id,)
        ).fetchone()

        if not row:
            raise ValueError('Source stock lot not found.')

        ndc, available, stock_exp = row

        if available < quantity:
            raise ValueError(
                f'Only {available} units available in source stock.'
            )

        if stock_exp < created.isoformat():
            raise ValueError(
                'Cannot make an amber vial from expired stock.'
            )

        # The vial cannot outlast its source stock expiration.
        expiry = min(
            months_after(created, 6).isoformat(),
            stock_exp
        )

        db.execute(
            '''UPDATE stock_lots
               SET quantity=quantity-?
               WHERE id=?''',
            (quantity, stock_id)
        )

        cursor = db.execute(
            '''INSERT INTO amber_vials
               (ndc,source_stock_id,created_date,
                expiration_date,quantity)
               VALUES(?,?,?,?,?)''',
            (
                ndc,
                stock_id,
                created.isoformat(),
                expiry,
                quantity
            )
        )

        vial_id = cursor.lastrowid

        # Record both sides of the transfer for traceability.
        record(
            db,
            'TRANSFER',
            'STOCK',
            stock_id,
            ndc,
            -quantity,
            f'To amber vial #{vial_id}'
        )

        record(
            db,
            'TRANSFER',
            'AMBER',
            vial_id,
            ndc,
            quantity,
            f'From stock #{stock_id}'
        )

        return vial_id, expiry


def adjust_vial(vial_id, change):
    """Remove individual units from an existing amber vial.

    Amber vials cannot receive additional units through this
    function. New vial inventory must originate from a stock
    transfer using create_amber_vial().

    Args:
        vial_id (int): Identifier of the amber vial.
        change (int): Negative quantity adjustment.

    Returns:
        int: Remaining units in the vial.

    Raises:
        ValueError: If the vial is missing, the adjustment is
        nonnegative, or insufficient units remain.
    """
    with connect_db() as db:
        db.execute('BEGIN IMMEDIATE')

        row = db.execute(
            '''SELECT ndc,quantity,expiration_date
               FROM amber_vials WHERE id=?''',
            (vial_id,)
        ).fetchone()

        if not row:
            raise ValueError('Amber vial not found.')

        ndc, qty, expiry = row

        if change >= 0:
            raise ValueError(
                'Use Create Amber Vial to transfer stock into vials.'
            )

        if qty + change < 0:
            raise ValueError('Insufficient amber vial units.')

        db.execute(
            '''UPDATE amber_vials
               SET quantity=quantity+?
               WHERE id=?''',
            (change, vial_id)
        )

        record(
            db,
            'OUT',
            'AMBER',
            vial_id,
            ndc,
            change,
            'Scanner'
        )

        return qty + change


def process_scan(raw):
    """Interpret a scanner command and adjust the selected inventory.

    Supported formats:
        IN:NDC|LOT   - Add one unit to a matching stock lot.
        OUT:NDC|LOT  - Remove one unit from a matching stock lot.
        IN:STOCK-12  - Add one unit to stock lot ID 12.
        OUT:STOCK-12 - Remove one unit from stock lot ID 12.
        OUT:VIAL-123 - Remove one unit from amber vial ID 123.

    An NDC without a lot number is accepted only when it
    identifies exactly one stock lot.

    Args:
        raw (str): Scanner command or manually entered text.

    Returns:
        str: Confirmation containing the item ID and remaining
        quantity.

    Raises:
        ValueError: If the command is invalid, ambiguous, or
        cannot be completed by the corresponding adjustment.
    """
    prefix, sep, payload = raw.strip().partition(':')
    action = prefix.upper()

    if not sep or action not in ('IN', 'OUT'):
        raise ValueError(
            'Use IN:NDC|LOT or OUT:NDC|LOT, or OUT:VIAL-123.'
        )

    payload = payload.strip()

    # Amber vial scans support removal only.
    if payload.upper().startswith('VIAL-'):
        if action != 'OUT':
            raise ValueError(
                'Vials can only be created by transferring stock.'
            )

        vial_id = int(payload[5:])

        return (
            f'AMBER vial #{vial_id}: '
            f'{adjust_vial(vial_id, -1)} units remain'
        )

    # Direct stock ID scans avoid ambiguity between multiple lots.
    if payload.upper().startswith('STOCK-'):
        stock_id = int(payload[6:])

        return (
            f'STOCK #{stock_id}: '
            f'{adjust_stock(stock_id, 1 if action == "IN" else -1)} '
            'units remain'
        )

    # Resolve an NDC and optional lot number to one stock record.
    ndc, delimiter, lot = payload.partition('|')

    if not valid_ndc(ndc):
        raise ValueError('Invalid 11-digit NDC.')

    with connect_db() as db:
        rows = db.execute(
            'SELECT id FROM stock_lots WHERE ndc=?'
            + (' AND lot_number=?' if delimiter else ''),
            (ndc, lot) if delimiter else (ndc,)
        ).fetchall()

    if len(rows) != 1:
        raise ValueError(
            'Stock scan must identify exactly one lot; '
            'use NDC|LOT or STOCK-ID.'
        )

    stock_id = rows[0][0]

    return (
        f'STOCK #{stock_id}: '
        f'{adjust_stock(stock_id, 1 if action == "IN" else -1)} '
        'units remain'
    )


def migrate_legacy_rows(metadata):
    """Import legacy medication records into the new inventory schema.

    Preserve the original medications table and import its records
    into products and stock_lots. Metadata must supply strength
    and package size for every legacy NDC.

    The migration uses one database transaction so validation
    failures roll back the attempted import.

    Args:
        metadata (dict): Mapping of NDC strings to tuples containing
            medication strength and package size.

    Returns:
        int: Number of legacy rows processed.

    Raises:
        ValueError: If required metadata is missing, product
        identities conflict, or a legacy row uses the reserved
        amber vial lot number 00000000.
    """
    with connect_db() as db:
        db.execute('BEGIN IMMEDIATE')

        present = db.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type='table' AND name='medications'"
        ).fetchone()

        if not present:
            return 0

        rows = db.execute(
            '''SELECT id,name,brand,ndc,expiration_date,
                      lot_number,quantity
               FROM medications'''
        ).fetchall()

        for _, name, brand, ndc, exp, lot, qty in rows:
            if ndc not in metadata:
                raise ValueError(
                    f'Missing strength/package size for NDC {ndc}. '
                    'No records imported.'
                )

            strength, size = metadata[ndc]

            existing = db.execute(
                '''SELECT name,brand,strength,package_size
                   FROM products WHERE ndc=?''',
                (ndc,)
            ).fetchone()

            proposed = (name, brand, strength, size)

            if existing and tuple(
                value.casefold() for value in existing
            ) != tuple(
                value.casefold() for value in proposed
            ):
                raise ValueError(
                    f'Conflicting NDC {ndc}; '
                    'resolve legacy records first.'
                )

            if not existing:
                db.execute(
                    'INSERT INTO products VALUES(?,?,?,?,?)',
                    (ndc, *proposed)
                )

            # Legacy rows using the vial lot number require review.
            if lot == '00000000':
                raise ValueError(
                    'Legacy lot 00000000 requires '
                    'manual amber-vial review.'
                )

            # Preserve any stock lot already imported.
            db.execute(
                '''INSERT INTO stock_lots
                   (ndc,lot_number,expiration_date,quantity)
                   VALUES(?,?,?,?)
                   ON CONFLICT(ndc,lot_number,expiration_date)
                   DO NOTHING''',
                (ndc, lot, exp, qty)
            )

        return len(rows)


if __name__ == '__main__':
    # Initialize the database when this module is run directly.
    create_database()

    print('Database initialized:', DATABASE)
    print('Legacy records requiring review:', legacy_status())
