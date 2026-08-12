// OnSubmit.gs
// Handlers for Intake and Withdrawal form submissions

function handleIntake_(e) {
  const map = normalizeFormMap_(e);
  const qty = Math.abs(Number(map['Quantity'] || 0) || 0);
  const files = map['Upload BOL / Packing Slip (PDF or Image)'] || '';
  const fileIds = extractFileIds_(files);

  // Move files to organized folders and collect links
  const links = routeIntakeFiles_(map.JobNumber, map.Subcontractor, fileIds);

  appendTransaction_({
    type: 'Intake',
    itemCode: map['Item / Material Code'],
    qty: qty,
    jobNumber: map.JobNumber,
    subcontractor: map.Subcontractor,
    fileLinks: links,
    editorEmail: map.__email
  });
}

function handleWithdrawal_(e) {
  const map = normalizeFormMap_(e);
  const qty = Math.abs(Number(map['Quantity'] || 0) || 0);
  const onHand = getOnHand_(map['Item / Material Code']);
  if (qty > onHand) {
    appendException_({
      type: 'Withdrawal',
      itemCode: map['Item / Material Code'],
      qty: qty,
      jobNumber: map.JobNumber,
      subcontractor: map.Subcontractor,
      editorEmail: map.__email
    }, 'Insufficient on-hand. Requested: ' + qty + ', OnHand: ' + onHand);
    notifyShortage_(map, onHand, qty);
    return;
  }
  appendTransaction_({
    type: 'Withdrawal',
    itemCode: map['Item / Material Code'],
    qty: -qty,
    jobNumber: map.JobNumber,
    subcontractor: map.Subcontractor,
    editorEmail: map.__email
  });
}

function normalizeFormMap_(e) {
  // e.namedValues: { Question: [answer] }
  const out = {};
  const nv = e && e.namedValues ? e.namedValues : {};
  Object.keys(nv).forEach(k => {
    const v = nv[k];
    out[k] = Array.isArray(v) ? v.join(', ') : v;
  });
  // Common
  out.JobNumber = out['Job Number'] || '';
  out.Subcontractor = out['Subcontractor'] || '';
  // Email (collector)
  out.__email = (e && e.response && e.response.getRespondentEmail) ? e.response.getRespondentEmail() : '';
  return out;
}

function extractFileIds_(fileAnswer) {
  // File upload items appear as Drive links; e.g., "MyFile.pdf (https://drive.google.com/open?id=FILE_ID)"
  if (!fileAnswer) return [];
  const out = [];
  const reIds = /[?&]id=([A-Za-z0-9_\-]+)/g;
  const reShare = /https:\/\/drive\.google\.com\/file\/d\/([A-Za-z0-9_\-]+)/g;
  const parts = fileAnswer.split(/,\s*/);
  parts.forEach(p => {
    let m;
    while ((m = reIds.exec(p)) !== null) out.push(m[1]);
    while ((m = reShare.exec(p)) !== null) out.push(m[1]);
  });
  return out;
}

function notifyShortage_(map, onHand, requested) {
  const to = getConfig_('ADMIN_EMAIL') || Session.getActiveUser().getEmail();
  const subject = '[Inventory Alert] Withdrawal Blocked - Insufficient Stock';
  const body = [
    'A withdrawal was blocked due to insufficient stock.\n',
    'ItemCode: ' + map['Item / Material Code'],
    'JobNumber: ' + map.JobNumber,
    'Subcontractor: ' + map.Subcontractor,
    'Requested Qty: ' + requested,
    'On-Hand Qty: ' + onHand,
    'Submitted by: ' + (map.__email || 'unknown'),
    'Timestamp: ' + new Date()
  ].join('\n');
  GmailApp.sendEmail(to, subject, body);
}
