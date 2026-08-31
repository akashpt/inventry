# SKH Computers Accounts Soft Flow

This project now covers the requested modules from the attached requirement document.

## Step 1: Master Data
- Add customers from Customers.
- Add suppliers/merchants from Merchant.
- Add products/spare parts from Products.
- Add warehouses from Inventory > Warehouses.

## Step 2: Inventory And Warehouse
- Use Inventory > Stock Movements for stock receiving, transfer, adjustment, issue, and barcode/QR references.
- Completed stock movements automatically update Products stock quantity.
- Completed receiving, issuing, transfers, and adjustments also update Inventory > Stock Balance by warehouse.
- Use Products stock quantity, Inventory > Stock Balance, and Reports stock summaries for stock monitoring.
- Stock reductions are blocked when the source warehouse does not have enough quantity.

## Step 3: Refurbishment And Production
- Register every incoming laptop/device in Production > Device Intake.
- Track model, serial number, supplier status, technician, QC status, estimated cost, and actual cost.
- Use Production > Tasks / QC for checking, repair tracking, parts used, QC assignment, and completion status.
- Completed production tasks can issue spare parts from inventory.
- Ready refurbishment jobs can add the finished device to inventory when finished product and warehouse are selected.

## Step 4: Sales And Customer Flow
- Create quotation from Sales Flow > Quotations.
- Add product lines from Quote Items.
- Use Create Order on a quotation to convert it into Sales Flow > Sales Orders.
- Add or review sales order lines from Order Items.
- Use Delivery Note on a sales order to create dispatch tracking.
- Use Delivery Items to review dispatched product lines.
- Use Invoice on a sales order to create final billing and mark the order completed.
- Invoice Items keep product-level quantity, rate, discount, tax, and total. Invoice creation from a sales order issues stock for warehouse-selected order lines.

## Step 4A: Purchase And Supplier Flow
- Create supplier purchase orders from Purchases > Purchase Orders.
- Add product, quantity, cost, and destination warehouse from Purchase Items.
- Use Receive Stock on a purchase order to create stock receiving movements.
- Use Supplier Bill on a purchase order to create the payable bill.

## Step 5: Returns / RMA
- Register returned devices from Returns / RMA.
- Track customer, invoice, product, reason, approval status, repair/replacement resolution, assigned staff, and closure date.
- Use Approve and Close actions on the RMA list for the approval workflow.
- Approval records approval user/date and creates return history. If a default warehouse exists in Settings, approved product returns are added back to stock once.

## Step 6: Accounts And Cash
- Track investments, withdrawals, expenses, and petty cash under Payments.
- Track customer invoice payments from Payments Received.
- Use Customer Statement and Supplier Statement for balances.
- Dashboard totals show receivables, payables, cash balance, petty cash, open invoices, production, stock alerts, and returns.

## Step 7: Reports And Security
- Use Reports for inventory, stock, production, sales, and return summaries, with detail pages for each report type.
- Use User Roles for Management Full Access, Accountant, Sales Manager, and Sales Staff profiles.
- Use Audit Logs to track create, update, and delete activity for the new operational modules.
- Login, logout, registration, profile, change password, and settings pages are connected.
- Public registration only allows unrestricted role selection for the first account. Later public registrations are limited to Sales Staff; role changes happen in User Roles.
- Management has full access. Accountant, Sales Manager, and Sales Staff are restricted by role.
