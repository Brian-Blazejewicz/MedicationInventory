Medication Inventory

Python Desktop Application | Tkinter | SQLite | Inventory Management

IMPORTANT: 100% FABRICATED DEMONSTRATION DATA

ALL INVENTORY DATA IN THIS PROJECT IS COMPLETELY FABRICATED FOR EDUCATIONAL, SOFTWARE DEVELOPMENT, AND TESTING PURPOSES.

Every inventory record, medication quantity, stock lot, expiration date, transaction, amber vial entry, and sample identifier contained in this project is simulated. This includes the information displayed in the application, SQLite database, CSV files, and screenshots.

None of the inventory records represents actual pharmacy inventory, real dispensing activity, patient information, or verified medication records.

Some medication and brand names may correspond to real pharmaceutical products. However, their inclusion is strictly for demonstration purposes. The associated identifiers, strengths, quantities, package sizes, lot numbers, expiration dates, and transaction details must not be interpreted as authentic, accurate, or verified pharmaceutical information.

This application is not approved, validated, or intended for use in a real pharmacy or healthcare environment. It must not be used for medication dispensing, patient care, inventory management in an operating pharmacy, recall decisions, or any other clinical or operational purpose.

The application demonstrates software functionality only.

Project Overview

Medication Inventory is a desktop application I developed using Python, Tkinter, and SQLite to organize medication inventory records, track expiration dates, and maintain a history of inventory changes.

The idea for this project came from my experience working in a pharmacy. Throughout a typical workday, there are situations where I need to check medication quantities, locate specific lot numbers, or identify products that are approaching their expiration dates. These tasks are important, but they can also take time, especially during a busy shift.

I wanted to explore how a desktop application could make this type of information easier to access while giving me an opportunity to apply the programming and database skills I have developed throughout my computer science education.

The application uses an entirely fabricated dataset to demonstrate inventory management concepts without relying on actual workplace records.

Project Features

The application includes several features designed around common medication inventory tasks.

Combined Inventory: Displays the total number of individual medication units by National Drug Code (NDC), including stock bottles, boxes, and amber vials.

Medication Search: Allows users to search for products by NDC, medication name, or brand.

Stock Management: Tracks individual stock lots, including their lot numbers, expiration dates, and available quantities.

Amber Vial Management: Allows inventory to be transferred from stock bottles or boxes into amber vials while maintaining accurate combined quantities.

Expiration Monitoring: Identifies inventory records with expiration dates within the next three months.

Scanner Input: Supports inventory adjustments through application-specific scanner-style commands.

Transaction History: Records inventory additions, removals, and transfers.

Sortable Tables: Makes it easier to organize and review inventory information.

All of these features operate on simulated inventory records. Their presence does not establish that the application is suitable for actual pharmacy operations.

Application Screenshots

Important: All information shown in the following screenshots is fabricated demonstration data. The screenshots do not represent actual pharmacy inventory, medication dispensing, stock transactions, or verified pharmaceutical records.

Combined Medication Inventory

The Combined by NDC tab displays medication information and total quantities across stock bottles, boxes, and amber vials.

Users can search for medications by NDC, medication name, or brand. The interface also provides access to the expiration monitoring report.



Stock Bottles and Boxes

The Stock bottles / boxes tab allows users to register medication products, create stock lots, and process inventory adjustments.

Each stock record includes a medication identifier, product information, lot number, expiration date, and available quantity.



Amber Vial Management

The Amber vials tab demonstrates how medication units can be transferred from an existing stock lot into a separate vial record.

When a transfer occurs, the application decreases the source stock quantity and increases the amber vial quantity by the same amount. This maintains the combined inventory total.



Transaction History

The Transactions tab displays inventory movements, including additions, removals, and transfers between stock lots and amber vials.

Each transaction includes a timestamp, movement type, associated inventory record, quantity change, and description.



Expiration Monitoring

The Expiring within 3 months report identifies simulated stock lots and amber vials with available quantities and expiration dates approaching within the selected three-month period.

This feature demonstrates how software could help organize expiration-related inventory reviews.



All screenshot data is synthetic. Dates, quantities, lot numbers, medication identifiers, and transaction records are not actual pharmacy information.

How This Project Relates to My Pharmacy Experience

One of the main reasons I wanted to develop this application was to create something that relates directly to my day-to-day responsibilities at work.

Working in a pharmacy has helped me understand how important accurate inventory information can be. Even relatively simple tasks, such as locating a particular medication lot or checking expiration dates, can become time-consuming when there are many products to manage.

This project gave me an opportunity to think about those challenges from a software development perspective.

Rather than using actual pharmacy records, I created a demonstration environment with fabricated inventory data to explore how these tasks might be organized through software.

Identifying Medications That Are Expiring Soon

One feature I wanted to include was the ability to quickly identify medications that are approaching their expiration dates.

In a pharmacy, checking expiration dates is an important part of maintaining inventory. However, manually reviewing bottles and boxes can take a considerable amount of time, especially when inventory is spread across multiple locations.

The application includes an Expiring within 3 months report that displays stock bottles, boxes, and amber vials with available quantities that are approaching their recorded expiration dates.

I believe a properly validated feature like this could be useful in my daily work because it would provide a starting point for identifying products that need attention.

Instead of checking every item individually just to determine what might be expiring soon, I could review a list of potentially affected medications and prioritize which products to physically inspect.

It could also help with inventory rotation and identifying products that may need to be reviewed before they expire.

For this project, the expiration dates and inventory records are entirely fabricated. The report demonstrates the programming logic and interface functionality, not the expiration status of any actual medication.

Any real-world implementation would still require physical verification, appropriate controls, and compliance with established pharmacy procedures.

Tracking and Locating Medication Lot Numbers

Another important part of pharmacy inventory management is keeping track of medication lot numbers.

Different bottles of the same medication can have different lot numbers and expiration dates. Being able to distinguish between them is useful when reviewing inventory, investigating discrepancies, or identifying products affected by a recall.

The application currently displays lot numbers alongside medication information, expiration dates, and quantities in the Stock bottles / boxes tab.

One improvement I would like to make is adding the ability to search directly by lot number.

For example, if a pharmacy receives a recall notice identifying a specific medication lot, a properly validated lot-number search feature could help staff identify matching inventory records for further review.

This could also be useful when checking a shipment or trying to determine which stock lot contains a particular quantity.

Although direct lot-number searching is not yet implemented, it is one of the features I would like to add as the project continues to develop.

All lot numbers currently used in this project are fabricated and do not identify actual medication lots.

Improving My Daily Workflow

Another goal of this project was to bring several inventory-related tasks into one application.

Instead of keeping track of stock quantities, amber vial transfers, expiration dates, and transaction records separately, the application organizes this information into different tabs.

I think having these features together could make it easier to review inventory changes and identify potential issues.

For example, if I transfer 20 simulated units from a stock bottle into an amber vial, the application automatically subtracts those units from the original stock and adds them to the new vial.

The total quantity remains the same, and the transfer is recorded in the transaction history.

This is the type of functionality I wanted to explore because it reflects how inventory moves between different forms of storage in a pharmacy.

Developing this project has also helped me better understand how software can be designed around the needs of the people using it.

Before a system like this could be used in an actual pharmacy, it would require extensive additional testing, security measures, validation, and review of applicable workplace and regulatory requirements.

Technologies Used

Technology

Purpose

Python 3

Main programming language

Tkinter

Desktop graphical user interface

SQLite

Local database management

SQL

Storing, retrieving, and updating inventory records

Python datetime and calendar

Expiration date calculations

The application uses Python's standard library and does not require additional third-party Python packages. Tkinter must be available in the Python installation.

Getting Started

Requirements

Python 3

Tkinter support

Windows, macOS, or Linux

The project files downloaded from this repository

Installation

Clone the repository using Git:

git clone https://github.com/Brian-Blazejewicz/MedicationInventory.git

Navigate to the project directory:

cd MedicationInventory

Run the application:

python medication_gui.py

On Windows, you can also use:

py medication_gui.py

The application opens a desktop window containing the inventory management interface.

If medications.db does not already exist in the project directory, the application creates a new SQLite database with the necessary tables. A newly created database will not contain sample inventory records.

The product_details.csv file contains supporting demonstration metadata but is not automatically imported when the application starts.

Do not import real pharmacy inventory records or patient information into this demonstration application.

Using the Application

Registering a Medication

Before adding inventory, a demonstration medication product must be registered in the database.

Under the Stock bottles / boxes tab, enter the following information:

11-digit National Drug Code (NDC)

Medication name

Brand

Strength

Package size

Select Register product to save the medication information.

All information entered for testing should be fabricated.

Adding a Stock Lot

After registering a demonstration medication, enter its NDC, lot number, and expiration date.

Expiration dates must use the following format:

YYYY-MM-DD

Select Add stock lot to create the inventory record.

New stock lots begin with a quantity of zero. Inventory can then be added through the scanner input.

Adding and Removing Inventory

The application accepts scanner-style commands to update simulated medication quantities.

Command

Function

IN:12345678901|LOT123

Add one unit to a specific stock lot

OUT:12345678901|LOT123

Remove one unit from a specific stock lot

IN:STOCK-12

Add one unit to stock record 12

OUT:STOCK-12

Remove one unit from stock record 12

OUT:VIAL-123

Remove one unit from amber vial 123

Each command adjusts the inventory by one individual simulated medication unit.

The example NDC, lot number, and stock IDs are placeholders. Actual commands must match demonstration records in the database.

These commands use an application-specific format and do not automatically interpret standard manufacturer barcodes.

Creating an Amber Vial

The Amber vials tab allows simulated units to be transferred from an existing stock lot into a new amber vial.

To create a vial:

Enter the source stock ID.

Enter the number of units to transfer.

Select Create Amber Vial.

Review the newly generated vial information.

The application checks whether the source stock exists, has enough units, and is not expired according to its stored demonstration data.

New amber vials receive the lot number 00000000.

Their expiration dates are calculated using the earlier of six calendar months from the creation date or the original stock expiration date.

This is a demonstration rule implemented in the application and must not be treated as an approved expiration or beyond-use dating policy for actual medications.

For example, if a simulated stock bottle contains 100 units and 20 are transferred into an amber vial, the updated inventory would be:

Inventory location

Quantity

Original stock

80

Amber vial

20

Combined inventory

100

This allows the application to track where simulated medication units are stored without counting the same units twice.

Application Interface

The interface is divided into four main tabs.

Combined by NDC

This tab displays medication information and combined quantities across stock bottles, boxes, and amber vials.

Users can search by NDC, medication name, or brand. The tab also includes the Expiring within 3 months report.

Stock Bottles / Boxes

This tab is used to register demonstration medications, create stock lots, process inventory scans, and review individual stock records.

Each stock record includes its lot number, expiration date, and quantity.

Amber Vials

This tab is used to transfer simulated inventory from stock lots into amber vials and review the resulting vial records.

It displays the source stock ID, vial lot number, creation date, expiration date, and remaining quantity.

Transactions

This tab displays the 500 most recent inventory movements, including additions, removals, and stock-to-vial transfers.

Having a transaction history makes it easier to review how simulated inventory quantities have changed over time.

Database Structure

The application uses SQLite to store inventory information locally.

The database includes four main tables.

Table

Description

products

Stores demonstration medication information associated with each NDC

stock_lots

Tracks simulated stock lots, quantities, and expiration dates

amber_vials

Tracks simulated medication units transferred into amber vials

movements

Records simulated inventory transactions and transfers

An additional SQL view called inventory_totals calculates the combined quantity for each medication.

I separated the database into these tables to keep the information organized and make it easier to manage the relationships between products, stock lots, and amber vials.

The database is a simulated testing environment. Its contents are not authentic pharmacy inventory records.

Project Files

File

Description

medication_gui.py

Contains the Tkinter interface

medication_inventory.py

Handles database operations and inventory logic

medications.db

SQLite database containing fabricated demonstration records, when present

product_details.csv

Fabricated supporting medication metadata

README.md

Project documentation

.gitignore

Excludes generated and local development files

screenshots/

Screenshots showing the application with fabricated data

Future Improvements

There are several features I would like to add as I continue developing the application.

Lot-number search: Allow users to locate demonstration inventory directly by entering a specific lot number.

Advanced filtering: Add more options for sorting and filtering medications by expiration date, quantity, or inventory location.

Improved reporting: Create additional reports for low inventory, upcoming expirations, and inventory activity.

Barcode integration: Expand scanner support to interpret standard barcode formats.

Interface improvements: Continue refining the layout and usability based on common pharmacy workflows.

Automated testing: Add unit tests for inventory adjustments, transfers, validation, and expiration calculations.

These additions would help make the application more useful as a demonstration of inventory management software.

What I Learned

Working on this project allowed me to combine my pharmacy experience with the programming skills I have developed while studying computer science.

I gained more experience building graphical interfaces with Tkinter, working with SQLite databases, writing SQL queries, validating user input, and organizing code into separate components.

One of the more interesting parts of the project was figuring out how to transfer inventory between stock bottles and amber vials without changing the overall medication quantity. I also wanted to make sure those transfers could be reviewed through a transaction history.

I also learned more about using fabricated datasets to test application functionality without involving real workplace information.

More importantly, this project helped me think about how software can address problems that people encounter in their everyday jobs.

I plan to continue improving the application as I learn more about software development, database management, and application design.

Author

Brian Blazejewicz

Computer Science Student
Southern New Hampshire University

GitHub: Brian-Blazejewicz

Final Disclaimer: Fabricated Data and Educational Use Only

EVERY INVENTORY RECORD AND ASSOCIATED DATA VALUE IN THIS PROJECT IS FABRICATED.

This includes all sample NDCs, medication identifiers, quantities, lot numbers, expiration dates, stock records, amber vial records, inventory transactions, and information displayed in screenshots.

Medication and brand names may resemble actual products, but no associated sample record should be interpreted as verified pharmaceutical information.

This project does not represent real pharmacy inventory, actual medication dispensing, patient records, or operational pharmacy activity.

The application was developed solely for educational purposes, programming practice, software testing, and demonstration within a computer science portfolio.

It has not been clinically validated and must not be used to make medication-related decisions or manage actual pharmacy operations.

All project data is simulated. No information in this repository should be relied upon for patient care, medication dispensing, recall management, or real-world pharmaceutical inventory decisions.
