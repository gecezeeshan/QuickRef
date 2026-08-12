// Config.gs
// Central config + helper for reading/writing IDs after Setup.install()

const CONFIG = {
  ADMIN_EMAIL: Session.getActiveUser().getEmail() || 'you@example.com', // change if needed
  // The following are written by Setup.install() and used thereafter
  MASTER_SPREADSHEET_ID: '',
  INTAKE_FORM_ID: '',
  WITHDRAWAL_FORM_ID: '',
  DRIVE_ROOT_FOLDER_ID: '',
  INTAKE_UPLOAD_ROOT_ID: '',

  // Named ranges used in Sheets
  RANGES: {
    CONFIG_TABLE: 'Config!A:B',
  }
};

function setConfig_(key, value) {
  const ss = SpreadsheetApp.openById(getConfig_('MASTER_SPREADSHEET_ID'));
  const sh = ss.getSheetByName('Config');
  const data = sh.getRange(1,1,sh.getLastRow(),2).getValues();
  let found = false;
  for (let i=0;i<data.length;i++) {
    if (data[i][0] === key) {
      sh.getRange(i+1,2).setValue(value);
      found = true;
      break;
    }
  }
  if (!found) {
    sh.appendRow([key, value]);
  }
}

function getConfig_(key) {
  if (key in CONFIG && CONFIG[key]) return CONFIG[key];
  // fallback: read from Config sheet if master exists
  try {
    const props = PropertiesService.getScriptProperties();
    const cached = props.getProperty(key);
    if (cached) return cached;
  } catch(_) {}
  return '';
}

function cacheConfig_(map) {
  const props = PropertiesService.getScriptProperties();
  props.setProperties(map, true);
}
