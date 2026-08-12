// Setup.gs
// Creates Sheets, Forms, Folders, Triggers, and writes IDs into Config sheet.

function install() {
  const ss = createMaster_();
  const masterId = ss.getId();
  Logger.log('Master Spreadsheet: ' + ss.getUrl());

  const drive = createDriveFolders_();
  Logger.log('Root Docs Folder: https://drive.google.com/drive/folders/' + drive.rootId);

  const intake = createIntakeForm_(masterId);
  Logger.log('Intake Form: ' + intake.url);

  const withdrawal = createWithdrawalForm_(masterId);
  Logger.log('Withdrawal Form: ' + withdrawal.url);

  embedQRToForm_(intake.form, intake.url);
  embedQRToForm_(withdrawal.form, withdrawal.url);

  createTriggers_(intake.form.getId(), withdrawal.form.getId());

  // Persist IDs to Config sheet and script properties
  const ids = {
    MASTER_SPREADSHEET_ID: masterId,
    INTAKE_FORM_ID: intake.form.getId(),
    WITHDRAWAL_FORM_ID: withdrawal.form.getId(),
    DRIVE_ROOT_FOLDER_ID: drive.rootId,
    INTAKE_UPLOAD_ROOT_ID: drive.intakeRootId
  };
  writeConfigToSheet_(ids);
  cacheConfig_(ids);
  Logger.log('Install complete.');
}

function writeConfigToSheet_(ids) {
  const ss = SpreadsheetApp.openById(ids.MASTER_SPREADSHEET_ID);
  const sh = ss.getSheetByName('Config');
  Object.keys(ids).forEach(k => {
    setConfig_(k, ids[k]);
  });
}

function rebuildQR() {
  const intakeId = getConfig_('INTAKE_FORM_ID');
  const withdrawalId = getConfig_('WITHDRAWAL_FORM_ID');
  if (!intakeId || !withdrawalId) throw new Error('Forms not found in config.');
  const intakeForm = FormApp.openById(intakeId);
  const withdrawalForm = FormApp.openById(withdrawalId);
  embedQRToForm_(intakeForm, intakeForm.getEditUrl().replace('edit', 'viewform'));
  embedQRToForm_(withdrawalForm, withdrawalForm.getEditUrl().replace('edit', 'viewform'));
}

function resetDemo() {
  const ss = SpreadsheetApp.openById(getConfig_('MASTER_SPREADSHEET_ID'));
  ['Transactions','Exceptions'].forEach(name => {
    const sh = ss.getSheetByName(name);
    if (sh) sh.getRange(2,1,Math.max(0, sh.getLastRow()-1), sh.getLastColumn()).clearContent();
  });
}

function createMaster_() {
  const ss = SpreadsheetApp.create('Master Inventory');
  // Sheets: Transactions, Inventory, ByJobNumber, BySubcontractor, Config, Exceptions
  const shTx = ss.getActiveSheet().setName('Transactions');
  shTx.appendRow(['Timestamp','Type','ItemCode','Qty','JobNumber','Subcontractor','FileLinks','EditorEmail']);

  const shInv = ss.insertSheet('Inventory');
  const shJob = ss.insertSheet('ByJobNumber');
  const shSub = ss.insertSheet('BySubcontractor');
  const shCfg = ss.insertSheet('Config');
  const shExc = ss.insertSheet('Exceptions');
  shExc.appendRow(['Timestamp','Type','ItemCode','Qty','JobNumber','Subcontractor','Reason','EditorEmail']);

  // Config header
  shCfg.appendRow(['Key','Value']);

  // Inventory formula (live on-hand per ItemCode)
  // Unique item codes
  shInv.getRange('A1').setValue('ItemCode');
  shInv.getRange('B1').setValue('OnHand');
  shInv.getRange('A2').setFormulaR1C1('=SORT(UNIQUE(FILTER(Transactions!C3, Transactions!C3<>"")))');
  // Sum qty by item
  shInv.getRange('B2').setFormulaR1C1('=ARRAYFORMULA(IF(R2C1:R<>"" , IFNA(VLOOKUP(R2C1:R, QUERY(Transactions!C3:C4, "select C, sum(D) group by C", 0), 2, FALSE), 0), ))');

  // ByJobNumber
  shJob.getRange('A1').setValue('ItemCode');
  shJob.getRange('B1').setValue('JobNumber');
  shJob.getRange('C1').setValue('NetQty');
  shJob.getRange('A2').setFormula('=QUERY(Transactions!C3:G, "select C, E, sum(D) where C is not null group by C, E label sum(D) \"NetQty\"", 0)');

  // BySubcontractor
  shSub.getRange('A1').setValue('ItemCode');
  shSub.getRange('B1').setValue('Subcontractor');
  shSub.getRange('C1').setValue('NetQty');
  shSub.getRange('A2').setFormula('=QUERY(Transactions!C3:G, "select C, F, sum(D) where C is not null group by C, F label sum(D) \"NetQty\"", 0)');

  return ss;
}

function createDriveFolders_() {
  const root = DriveApp.createFolder('Inventory-Docs');
  const intakeRoot = root.createFolder('Intake');
  return { rootId: root.getId(), intakeRootId: intakeRoot.getId() };
}

function createIntakeForm_(masterId) {
  const form = FormApp.create('Inventory Intake');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, masterId); // responses go to a Responses sheet, not used here for logic
  form.setCollectEmail(true);
  form.setAllowResponseEdits(false);

  // Questions
  form.addTextItem().setTitle('Item / Material Code').setRequired(true);
  form.addTextItem().setTitle('Job Number').setRequired(true);
  form.addTextItem().setTitle('Subcontractor').setRequired(true);
  form.addTextItem().setTitle('Quantity').setHelpText('Enter positive number').setRequired(true);
  const upload = form.addFileUploadItem();
  upload.setTitle('Upload BOL / Packing Slip (PDF or Image)').setHelpText('Uploads are stored in Drive.').setRequired(true);
  upload.setHelpText('Accepted: PDF, images (PNG/JPG). Max per file 10MB.');

  const url = form.getEditUrl().replace('edit', 'viewform');
  return { form, url };
}

function createWithdrawalForm_(masterId) {
  const form = FormApp.create('Inventory Withdrawal');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, masterId);
  form.setCollectEmail(true);
  form.setAllowResponseEdits(false);

  // Questions
  form.addTextItem().setTitle('Item / Material Code').setRequired(true);
  form.addTextItem().setTitle('Job Number').setRequired(true);
  form.addTextItem().setTitle('Subcontractor').setRequired(true);
  form.addTextItem().setTitle('Quantity').setHelpText('Enter positive number to withdraw').setRequired(true);

  const url = form.getEditUrl().replace('edit', 'viewform');
  return { form, url };
}

function embedQRToForm_(form, targetUrl) {
  // Use Google Chart API to embed QR as image item in the form
  const qrUrl = 'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl=' + encodeURIComponent(targetUrl);
  const imgBlob = UrlFetchApp.fetch(qrUrl).getBlob().setName('qr.png');
  // If an image already exists named "QR", remove it by simple strategy: forms API does not allow rename, so just append a fresh image on top
  form.addImageItem().setTitle('Scan to open form').setImage(imgBlob);
}

function createTriggers_(intakeFormId, withdrawalFormId) {
  // Remove existing triggers
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));

  ScriptApp.newTrigger('handleIntake_')
    .forForm(intakeFormId)
    .onFormSubmit()
    .create();

  ScriptApp.newTrigger('handleWithdrawal_')
    .forForm(withdrawalFormId)
    .onFormSubmit()
    .create();
}
