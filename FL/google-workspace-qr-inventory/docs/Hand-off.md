# Hand-off Guide

This document helps your team maintain and extend the QR-based Inventory solution.

## Where things live

- **Apps Script code**: in your Apps Script project (`src/*.gs`), manifest `appsscript.json`.
- **Master Inventory spreadsheet**: created by `Setup.install()`; open the URL printed in execution logs.
- **Google Forms**: Intake + Withdrawal created by `Setup.install()` (links printed in logs).
- **Drive root**: a top-level folder `Inventory-Docs/` for routed intake documents.

## Key Tabs (Master Spreadsheet)

- **Transactions**: append-only log of form submissions. Intake = positive qty, Withdrawal = negative qty.
- **Inventory**: calculates on-hand by ItemCode. Do not edit formulas.
- **ByJobNumber**: live aggregation by (ItemCode, JobNumber).
- **BySubcontractor**: live aggregation by (ItemCode, Subcontractor).
- **Config**: internal IDs for Forms, Triggers, and Folders (managed by script).

## Daily Ops

- Stock comes in → scan QR for **Intake** → upload BOL/packing slip → record ItemCode, Qty, JobNumber, Subcontractor.
- Stock goes out → scan QR for **Withdrawal** → record ItemCode, Qty, JobNumber, Subcontractor.
- Check **Inventory** tab for on-hand totals; drill down via **ByJobNumber**/**BySubcontractor** tabs.

## Negative Stock

- If a withdrawal would push on-hand below 0:
  - The transaction is **blocked** and listed on **Exceptions**.
  - An email alert is sent to `ADMIN_EMAIL` with the details.
  - To resolve: intake stock or reduce the withdrawal quantity, then resubmit.

## Changing Forms

- If you duplicate or move forms, run `Setup.rebuildQR()` to refresh the QR images.
- You can add new choices/validation to forms without breaking the sheet structure.
- Keep the file upload question **in the Intake Form** only.

## Extending

- Add part master data (description, UOM) in a new tab `Items` and use `VLOOKUP` in `Inventory` and views.
- Add per-location bins by adding a `Location` column to both forms, then include in `Transactions` and modify queries.
- Add Slack/Chat alerts by plugging into `OnSubmit` handlers alongside email.

