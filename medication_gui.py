
"""Tkinter interface for stock and amber-vial inventory management.

Display combined medication quantities, register stock, transfer units to
amber vials, process scanner input, and review recent transactions.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import medication_inventory as db


class InventoryApp:
    """Build and manage the Tkinter medication inventory interface."""

    def __init__(self, root):
        """Initialize the main window, inventory tabs, and displayed data."""
        self.root = root
        root.title('Medication Inventory — Stock and Amber Vials')
        root.geometry('1250x800')

        db.create_database()

        self.sort = {}
        self.tables = {}
        self.search = tk.StringVar()
        self.lot_search = tk.StringVar()
        self.status = tk.StringVar(
            value='Ready. Quantities are individual medication units.'
        )

        tk.Label(
            root,
            text='DEMONSTRATION ONLY — ALL DATA IS FABRICATED. NOT FOR PHARMACY USE, DISPENSING, OR PATIENT CARE.',
            fg='#8B0000', bg='#FFF0D9', font=('TkDefaultFont', 10, 'bold'),
            wraplength=1150, pady=9
        ).pack(fill='x', padx=10, pady=(8, 2))

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill='both', expand=True, padx=10, pady=8)

        self.build_all_tab()
        self.build_stock_tab()
        self.build_amber_tab()
        self.build_history_tab()

        ttk.Label(
            root,
            textvariable=self.status
        ).pack(fill='x', padx=12, pady=5)

        self.refresh()

    def field(self, parent, row, label, width=22):
        """Create a labeled text entry and return the entry widget."""
        ttk.Label(
            parent,
            text=label
        ).grid(row=row, column=0, sticky='w', padx=5, pady=3)

        entry = ttk.Entry(parent, width=width)
        entry.grid(
            row=row,
            column=1,
            sticky='ew',
            padx=5,
            pady=3
        )

        return entry

    def make_table(self, parent, key, columns, widths=None):
        """Create a scrollable table with sortable column headings.

        Store the Treeview under the supplied key for later refreshes.
        """
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True, padx=6, pady=6)

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        for i, col in enumerate(columns):
            tree.heading(
                col,
                text=col.replace('_', ' ').title(),
                command=lambda c=col, k=key: self.sort_by(k, c)
            )
            tree.column(
                col,
                width=(widths[i] if widths else 125),
                anchor='w'
            )

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        vertical = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        horizontal = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky='nsew')
        vertical.grid(row=0, column=1, sticky='ns')
        horizontal.grid(row=1, column=0, sticky='ew')

        self.tables[key] = tree
        return tree

    def build_all_tab(self):
        """Create the combined NDC inventory tab and search controls."""
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text='Combined by NDC')

        row = ttk.Frame(tab)
        row.pack(fill='x', padx=8, pady=8)

        ttk.Label(row, text='Search:').pack(side='left')
        search_entry = ttk.Entry(
            row,
            textvariable=self.search,
            width=35
        )
        search_entry.pack(side='left', padx=8)
        search_entry.bind('<Return>', lambda event: self.refresh())

        ttk.Button(
            row,
            text='Refresh',
            command=self.refresh
        ).pack(side='left')

        ttk.Button(
            row,
            text='Expiring within 3 months',
            command=self.expiring_report
        ).pack(side='left', padx=8)

        ttk.Button(
            row, text='Expired inventory',
            command=self.expired_report
        ).pack(side='left', padx=4)

        self.make_table(
            tab,
            'all',
            (
                'ndc', 'name', 'brand', 'strength', 'package_size',
                'stock_units', 'vial_units', 'total_units'
            ),
            (125, 170, 150, 110, 125, 100, 100, 100)
        )

    def build_stock_tab(self):
        """Create product registration, stock lot, and scanner controls."""
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text='Stock bottles / boxes')

        panel = ttk.LabelFrame(
            tab,
            text='Register a product (one identity per NDC)'
        )
        panel.pack(fill='x', padx=8, pady=6)

        self.product_fields = {}

        for i, label in enumerate(
            ('ndc', 'name', 'brand', 'strength', 'package_size')
        ):
            ttk.Label(
                panel,
                text=label.replace('_', ' ').title()
            ).grid(row=0, column=i, padx=4, sticky='w')

            entry = ttk.Entry(panel, width=23)
            entry.grid(row=1, column=i, padx=4, pady=4)
            self.product_fields[label] = entry

        ttk.Button(
            panel,
            text='Register product',
            command=self.register_product
        ).grid(row=1, column=5, padx=5)

        panel2 = ttk.LabelFrame(
            tab,
            text='Register stock lot (initial quantity 0)'
        )
        panel2.pack(fill='x', padx=8, pady=5)

        self.lot_ndc = self.field(panel2, 0, '11-digit NDC')
        self.lot_number = self.field(panel2, 1, 'Stock lot number')
        self.lot_exp = self.field(
            panel2, 2, 'Expiration YYYY-MM-DD'
        )

        ttk.Button(
            panel2,
            text='Add stock lot',
            command=self.add_lot
        ).grid(row=2, column=2, padx=8)

        scan = ttk.LabelFrame(
            tab,
            text='Bluetooth scanner: IN:NDC|LOT, OUT:NDC|LOT, '
                 'or IN:STOCK-12'
        )
        scan.pack(fill='x', padx=8, pady=6)

        self.scan_entry = ttk.Entry(scan, width=48)
        self.scan_entry.pack(side='left', padx=8, pady=6)
        self.scan_entry.bind(
            '<Return>',
            lambda event: self.scan()
        )

        ttk.Button(
            scan,
            text='Process scan',
            command=self.scan
        ).pack(side='left')

        lot_row = ttk.Frame(tab)
        lot_row.pack(fill='x', padx=8, pady=(3, 0))
        ttk.Label(lot_row, text='Find lot / NDC / medication:').pack(side='left')
        lot_entry = ttk.Entry(lot_row, textvariable=self.lot_search, width=35)
        lot_entry.pack(side='left', padx=8)
        lot_entry.bind('<Return>', lambda event: self.refresh())
        ttk.Button(lot_row, text='Search lots', command=self.refresh).pack(side='left')
        ttk.Button(lot_row, text='Clear', command=self.clear_lot_search).pack(side='left', padx=5)

        self.make_table(
            tab,
            'stock',
            (
                'id', 'ndc', 'name', 'brand', 'strength',
                'lot_number', 'expiration_date', 'quantity'
            )
        )

    def build_amber_tab(self):
        """Create controls for vial transfers and simulated inventory removal scans."""
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text='Amber vials')

        frame = ttk.LabelFrame(
            tab,
            text='Create vial by transferring units from a stock lot'
        )
        frame.pack(fill='x', padx=8, pady=8)

        self.source_id = self.field(frame, 0, 'Source stock ID')
        self.vial_qty = self.field(frame, 1, 'Units to transfer')

        ttk.Button(
            frame,
            text='Create Amber Vial',
            command=self.create_vial
        ).grid(row=2, column=1, pady=6)

        ttk.Label(
            frame,
            text='Lot 00000000; expiration: six calendar months '
                 'from today, capped at stock expiration.'
        ).grid(
            row=3,
            column=0,
            columnspan=3,
            padx=6,
            pady=5,
            sticky='w'
        )

        frame2 = ttk.LabelFrame(
            tab,
            text='Scan amber vial OUT:VIAL-123 (individual units)'
        )
        frame2.pack(fill='x', padx=8, pady=5)

        self.vial_scan = ttk.Entry(frame2, width=45)
        self.vial_scan.pack(side='left', padx=8, pady=5)
        self.vial_scan.bind(
            '<Return>',
            lambda event: self.scan(vial=True)
        )

        ttk.Button(
            frame2,
            text='Process vial scan',
            command=lambda: self.scan(vial=True)
        ).pack(side='left')

        self.make_table(
            tab,
            'amber',
            (
                'id', 'ndc', 'name', 'brand', 'strength',
                'source_stock_id', 'lot_number', 'created_date',
                'expiration_date', 'quantity'
            )
        )

    def build_history_tab(self):
        """Create the table displaying recent inventory movements."""
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text='Transactions')

        self.make_table(
            tab,
            'history',
            (
                'timestamp', 'kind', 'item_type', 'item_id',
                'ndc', 'delta', 'note'
            )
        )

    def sort_by(self, key, col):
        """Toggle the selected column's sort direction and refresh."""
        current = self.sort.get(key)
        self.sort[key] = (
            col,
            not current[1] if current and current[0] == col else False
        )
        self.refresh()

    def fill(self, key, rows):
        """Replace displayed rows and apply the active table sort."""
        tree = self.tables[key]

        for child in tree.get_children():
            tree.delete(child)

        sort = self.sort.get(key)

        if sort:
            col, descending = sort
            index = list(tree['columns']).index(col)

            def order(row):
                """Convert numeric columns for accurate sorting."""
                value = row[index]

                if col in (
                    'id', 'source_stock_id', 'item_id', 'quantity',
                    'stock_units', 'vial_units', 'total_units', 'delta'
                ):
                    return int(value)

                return str(value).casefold()

            rows = sorted(
                rows,
                key=order,
                reverse=descending
            )

        for row in rows:
            tree.insert('', 'end', values=row)

    def refresh(self):
        """Reload product totals, stock lots, vials, and movements.

        The search term filters combined product rows. The stock and
        amber tabs display all their rows, while transaction history
        is limited to the most recent 500 movements.
        """
        term = '%' + self.search.get().strip() + '%'

        with db.connect_db() as conn:
            all_rows = conn.execute(
                '''SELECT ndc, name, brand, strength, package_size,
                          stock_units, vial_units, total_units
                   FROM inventory_totals
                   WHERE ndc LIKE ? OR name LIKE ? OR brand LIKE ?
                   ORDER BY name, ndc''',
                (term, term, term)
            ).fetchall()

            stock = db.search_lots(self.lot_search.get())

            amber = conn.execute(
                '''SELECT a.id, a.ndc, p.name, p.brand, p.strength,
                          a.source_stock_id, a.lot_number,
                          a.created_date, a.expiration_date, a.quantity
                   FROM amber_vials a
                   JOIN products p ON p.ndc = a.ndc
                   ORDER BY a.id DESC'''
            ).fetchall()

            history = conn.execute(
                '''SELECT timestamp, kind, item_type, item_id,
                          ndc, delta, note
                   FROM movements
                   ORDER BY id DESC
                   LIMIT 500'''
            ).fetchall()

        for key, rows in (
            ('all', all_rows),
            ('stock', stock),
            ('amber', amber),
            ('history', history)
        ):
            self.fill(key, rows)

        self.status.set(
            f'{len(all_rows)} products; '
            f'{sum(r[7] for r in all_rows)} total individual units. '
            'Stock and amber vial quantities included.'
        )

    def clear_lot_search(self):
        self.lot_search.set('')
        self.refresh()

    def perform(self, fn):
        """Execute an action, refresh the GUI, and display handled errors."""
        try:
            result = fn()
            self.refresh()
            return result

        except (ValueError, sqlite3.Error) as exc:
            messagebox.showerror(
                'Cannot complete action',
                str(exc)
            )
            return None

    def register_product(self):
        """Submit the product registration fields to the backend."""
        self.perform(
            lambda: db.register_product(
                **{
                    key: entry.get()
                    for key, entry in self.product_fields.items()
                }
            )
        )

    def add_lot(self):
        """Submit a new stock lot to the database backend."""
        self.perform(
            lambda: db.add_stock_lot(
                self.lot_ndc.get().strip(),
                self.lot_number.get().strip(),
                self.lot_exp.get().strip()
            )
        )

    def create_vial(self):
        """Validate vial inputs, transfer stock, and display vial details.

        Require positive whole-number values for the source stock ID and
        transfer quantity. The backend checks availability and expiration.
        """
        source_text = self.source_id.get().strip()
        quantity_text = self.vial_qty.get().strip()

        if not source_text.isascii() or not source_text.isdecimal():
            messagebox.showerror(
                'Invalid stock ID',
                'Source stock ID must be a positive whole number.'
            )
            self.source_id.focus_set()
            return

        if not quantity_text.isascii() or not quantity_text.isdecimal():
            messagebox.showerror(
                'Invalid quantity',
                'Units to transfer must be a positive whole number.'
            )
            self.vial_qty.focus_set()
            return

        try:
            stock_id = db.parse_positive_id(source_text, 'Source stock ID')
            quantity = db.parse_positive_id(quantity_text, 'Transfer quantity')
        except ValueError as exc:
            messagebox.showerror('Invalid vial details', str(exc))
            return

        if stock_id <= 0 or quantity <= 0:
            messagebox.showerror(
                'Invalid vial details',
                'Source stock ID and units to transfer must be greater than zero.'
            )
            return

        # perform() refreshes the tables after a successful transfer.
        result = self.perform(
            lambda: db.create_amber_vial(stock_id, quantity)
        )

        if result is None:
            return

        vial_id, expiration = result
        messagebox.showinfo(
            'Amber vial created',
            f'Vial ID: {vial_id}\n'
            'Lot: 00000000\n'
            f'Expiration: {expiration}\n'
            f'Scan OUT:VIAL-{vial_id} for simulated removal (not dispensing).'
        )

    def scan(self, vial=False):
        """Process scanner input from the stock or amber vial tab."""
        field = self.vial_scan if vial else self.scan_entry
        raw = field.get().strip()
        field.delete(0, 'end')

        if not raw:
            return

        result = self.perform(
            lambda: db.process_scan(raw)
        )

        if result:
            self.status.set(result)

        field.focus_set()

    def expired_report(self):
        """Show positive-quantity records whose recorded expiry is in the past."""
        self.expiration_report(expired=True)

    def expiring_report(self):
        """Show positive-quantity records expiring in the next three months."""
        self.expiration_report(expired=False)

    def expiration_report(self, expired=False):
        """Display stock and amber records in an expiration-date window."""
        today = date.today().isoformat()
        cutoff = db.months_after(date.today(), 3).isoformat()
        where = 'expiration_date < ?' if expired else 'expiration_date BETWEEN ? AND ?'
        params = (today,) if expired else (today, cutoff)
        with db.connect_db() as conn:
            rows = conn.execute(
                f"""SELECT 'STOCK', s.id, s.ndc, p.name,
                           s.lot_number, s.expiration_date, s.quantity
                    FROM stock_lots s JOIN products p ON p.ndc=s.ndc
                    WHERE s.quantity > 0 AND s.{where}
                    UNION ALL
                    SELECT 'AMBER', a.id, a.ndc, p.name,
                           a.lot_number, a.expiration_date, a.quantity
                    FROM amber_vials a JOIN products p ON p.ndc=a.ndc
                    WHERE a.quantity > 0 AND a.{where}
                    ORDER BY 6""",
                params + params
            ).fetchall()
        title = 'Expired inventory' if expired else 'Expiring within 3 months'
        window = tk.Toplevel(self.root)
        window.title(title + ' — FABRICATED DEMO DATA')
        window.geometry('980x500')
        ttk.Label(window, text='SIMULATED DATA ONLY — NOT FOR PHARMACY USE').pack(pady=5)
        frame = ttk.Frame(window)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        cols = ('type', 'id', 'ndc', 'name', 'lot', 'expiration', 'units')
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col.title())
            tree.column(col, width=130)
        vertical = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        horizontal = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky='nsew')
        vertical.grid(row=0, column=1, sticky='ns')
        horizontal.grid(row=1, column=0, sticky='ew')
        for row in rows:
            tree.insert('', 'end', values=row)
        description = (f'before {today}' if expired else f'{today} through {cutoff} (inclusive)')
        ttk.Label(window, text=f'{len(rows)} simulated records: {description}').pack(pady=6)


if __name__ == '__main__':
    root = tk.Tk()
    InventoryApp(root)
    root.mainloop()
