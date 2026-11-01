
# Medication Inventory

### Python | Tkinter | SQLite | Unit Testing

A desktop inventory management application built with Python, Tkinter, and SQLite. This project demonstrates database management, graphical user interface development, inventory tracking, transaction logging, and automated software testing.

> **DEMONSTRATION ONLY — ALL DATA IS FABRICATED.**
>
> This application is an educational software project. It is **NOT intended for actual pharmacy inventory management, medication dispensing, or patient care.** Medication names, NDCs, lot numbers, and other sample records are for demonstration purposes only.

## Project Overview

Medication Inventory is a Python desktop application designed to simulate how a medication inventory system might organize products, track stock quantities, manage individual lots, and record inventory transactions.

The application separates stock bottles and boxes from amber vials, allowing users to simulate transferring quantities between different inventory containers while maintaining accurate totals.

The project was developed as part of my computer science portfolio to demonstrate practical software development skills, including Python programming, relational database design, input validation, error handling, and automated testing.

## Features

### Medication Product Management

- Register fabricated medication products using an 11-digit NDC.
- Store product names, brands, strengths, and package sizes.
- Prevent conflicting product details from being registered under the same NDC.
- Search inventory records by medication name, NDC, or lot number.

### Stock Bottles and Boxes

- Register stock lots with unique identifiers.
- Track lot numbers, expiration dates, and quantities.
- Increase or decrease simulated stock quantities.
- Prevent inventory quantities from becoming negative.
- Maintain separate records for different stock lots.

### Amber Vial Management

- Create simulated amber vials from existing stock.
- Transfer quantities from stock containers into amber vials.
- Preserve total inventory quantities during transfers.
- Associate amber vials with their source stock records.
- Calculate demonstration vial expiration dates using a six-calendar-month limit or the source stock expiration date, whichever occurs first.

The expiration calculation is a project simulation rule, not a clinical beyond-use dating recommendation.

### Barcode-Style Scanner Commands

The application supports manually entered scanner-style commands that simulate receiving and removing inventory.

Examples:

| Command | Action |
|---|---|
| `IN:12345678901|DEMO-LOT-001` | Add one unit to a matching stock lot |
| `OUT:12345678901|DEMO-LOT-001` | Remove one unit from a matching stock lot |
| `IN:STOCK-12` | Add one unit to stock record 12 |
| `OUT:STOCK-12` | Remove one unit from stock record 12 |
| `OUT:VIAL-123` | Remove one unit from amber vial 123 |

The stock and vial IDs above are examples. Actual IDs are assigned by the database.

### Expiration Tracking

- Identify stock that is already expired.
- Display inventory expiring within three calendar months.
- Track expiration dates for stock and amber vials.
- Reject certain invalid inventory operations involving expired stock.

### Transaction History

The application records simulated inventory changes in a SQLite transaction log.

Transaction information includes:

- Timestamp
- Transaction type
- Inventory record type and identifier
- Medication NDC
- Quantity change
- Transaction note

### Graphical User Interface

The application uses Tkinter to provide a desktop interface with four main tabs:

1. **Combined by NDC** — Displays aggregated inventory quantities by medication product.
2. **Stock Bottles/Boxes** — Displays individual stock lots and quantities.
3. **Amber Vials** — Displays simulated amber vial inventory.
4. **Transactions** — Displays recorded inventory movements.

The interface also provides search controls, scrolling tables, inventory actions, and expiration reports.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Tkinter | Desktop graphical user interface |
| SQLite | Local relational database |
| SQL | Data storage, queries, and aggregation |
| unittest | Automated software testing |
| unittest.mock | Isolation of test databases |
| tempfile | Temporary databases for testing |
| Git and GitHub | Version control and portfolio presentation |

The application primarily uses Python's standard library.

## Project Structure

```text
MedicationInventory/
│
├── medication_inventory.py
├── medication_gui.py
├── product_details.csv
├── README.md
├── requirements.txt
├── CHANGELOG.md
├── .gitignore
│
├── tests/
│   └── test_medication_inventory.py
│
└── screenshots/
    └── [application screenshots]
```

A local `medications.db` file is created or accessed by the application. This database is intended for local use and should not be committed to the repository.

The exact screenshot filenames may vary.

## Installation and Setup

### Prerequisites

- Windows, macOS, or Linux with Python installed
- Python 3.10 or newer recommended
- Tkinter support
- Git (optional, for cloning the repository)

### 1. Clone the Repository

```bash
git clone https://github.com/Brian-Blazejewicz/MedicationInventory.git
cd MedicationInventory
```

Alternatively, download the repository as a ZIP file from GitHub and extract it.

### 2. Verify Python

On Windows:

```cmd
py --version
```

On macOS or Linux:

```bash
python3 --version
```

### 3. Run the Application

On Windows:

```cmd
py medication_gui.py
```

On macOS or Linux:

```bash
python3 medication_gui.py
```

The application uses a local SQLite database. The required database tables are initialized when the application starts.

No external database server is required.

## Using the Application

### Registering a Medication

1. Launch the application.
2. Locate the product registration controls.
3. Enter a fabricated 11-digit NDC.
4. Enter the product name, brand, strength, and package size.
5. Register the product.

### Adding a Stock Lot

1. Select an existing medication product.
2. Enter a fabricated lot number.
3. Enter the expiration date.
4. Create the stock record.
5. Add simulated inventory quantities as needed.

### Creating an Amber Vial

1. Locate the source stock record.
2. Select the amber vial creation option.
3. Enter the quantity to transfer.
4. Confirm the transfer.
5. Review the updated stock and amber vial quantities.

The application decreases the source stock quantity and creates a corresponding amber vial record.

### Reviewing Transactions

Open the Transactions tab to review the history of simulated inventory changes.

## Automated Testing

The project includes **28 automated unit tests** using Python's built-in `unittest` framework.

The tests cover:

- Database table and view creation
- Product registration and duplicate handling
- NDC and expiration date validation
- Stock lot creation
- Stock quantity adjustments
- Prevention of negative inventory
- Scanner command processing
- Amber vial creation and transfers
- Preservation of inventory totals during transfers
- Vial expiration calculations
- Inventory searching
- Transaction history
- Input validation and error handling

### Running the Tests

From the project root directory, run:

**Windows:**

```cmd
py -m unittest discover -s tests -v
```

**macOS/Linux:**

```bash
python3 -m unittest discover -s tests -v
```

### Verified Test Results

The automated test suite was executed successfully on Windows.

```text
Ran 28 tests

OK
```

Each test uses a temporary SQLite database, helping isolate test data from the application's local inventory database.

## Screenshots

Screenshots of the application are stored in the `screenshots` directory.

They can demonstrate the following features:

- Combined inventory by NDC
- Stock bottles and boxes
- Amber vial management
- Inventory transactions
- Expiration reporting

Screenshots should show fabricated demonstration records only.

## Database Design

The SQLite database uses the following primary tables:

| Table | Description |
|---|---|
| `products` | Medication product information |
| `stock_lots` | Individual stock containers and quantities |
| `amber_vials` | Simulated transferred inventory |
| `movements` | Inventory transaction history |

An `inventory_totals` view combines stock and amber vial quantities by NDC.

The database design uses relationships between products, stock lots, and amber vials to help maintain consistent inventory records.

## Software Design

The application separates its major responsibilities into different files:

**medication_inventory.py**

Contains the database operations, input validation, stock adjustments, vial transfers, inventory searches, and scanner command processing.

**medication_gui.py**

Contains the Tkinter interface, user controls, tables, reports, and interactions with the backend.

**tests/test_medication_inventory.py**

Contains automated tests for the application's backend functionality.

This separation helps improve code organization, maintainability, and testability.

## Challenges and Lessons Learned

One challenge during development was maintaining accurate inventory quantities when transferring simulated stock into amber vials. The application needed to subtract quantities from the original stock record while preserving the overall inventory total.

Another challenge involved managing SQLite database connections during automated testing on Windows. The initial test run encountered file-locking errors because temporary databases were still open during cleanup. Updating the database connection management to close connections properly resolved the issue.

This project helped strengthen my understanding of:

- Relational database design
- Python application architecture
- GUI development
- Data validation
- Database transactions
- Automated unit testing
- Debugging and troubleshooting
- Organizing software for long-term maintenance

## Future Improvements

Potential enhancements include:

- Additional search and filtering options
- CSV import and export tools
- Inventory reports and printable summaries
- More extensive automated GUI testing
- Improved accessibility and keyboard navigation
- Additional inventory visualization features
- Configurable demonstration expiration rules

## Important Limitations

This project is an educational demonstration, not a validated pharmacy management system.

It does not provide:

- Clinical decision support
- Patient or prescription management
- Regulatory compliance verification
- Validated medication dispensing workflows
- Verified drug identification
- Clinical beyond-use dating
- Production-grade security, access control, or audit guarantees

**All inventory information must remain fabricated. Do not use this application for actual pharmacy inventory, medication dispensing, or patient care.**

## Author

**Brian Blazejewicz**

Computer Science Student  
Southern New Hampshire University

GitHub: https://github.com/Brian-Blazejewicz

Project Repository: https://github.com/Brian-Blazejewicz/MedicationInventory

## License

No license is specified unless a separate `LICENSE` file is added to the repository.
