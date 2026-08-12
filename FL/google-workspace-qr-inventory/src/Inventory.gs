// Inventory.gs
// Helpers to read current on-hand and to append to Transactions

function appendTransaction_(tx) {
  const ss = SpreadsheetApp.openById(getConfig_('MASTER_SPREADSHEET_ID'));
  const sh = ss.getSheetByName('Transactions');
  sh.appendRow([new Date(), tx.type, tx.itemCode, tx.qty, tx.jobNumber, tx.subcontractor, tx.fileLinks || '', tx.editorEmail || '']);
}

function appendException_(tx, reason) {
  const ss = SpreadsheetApp.openById(getConfig_('MASTER_SPREADSHEET_ID'));
  const sh = ss.getSheetByName('Exceptions');
  sh.appendRow([new Date(), tx.type, tx.itemCode, tx.qty, tx.jobNumber, tx.subcontractor, reason, tx.editorEmail || '']);
}

function getOnHand_(itemCode) {
  const ss = SpreadsheetApp.openById(getConfig_('MASTER_SPREADSHEET_ID'));
  const inv = ss.getSheetByName('Inventory');
  const values = inv.getRange(2,1,Math.max(0, inv.getLastRow()-1),2).getValues(); // [ItemCode, OnHand]
  for (let i=0;i<values.length;i++) {
    if (values[i][0] === itemCode) return Number(values[i][1]) || 0;
  }
  return 0;
}
