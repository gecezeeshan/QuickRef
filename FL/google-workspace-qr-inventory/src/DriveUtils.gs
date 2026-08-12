// DriveUtils.gs
// Moves intake upload files to structured folders and returns URL strings

function routeIntakeFiles_(jobNumber, subcontractor, fileIds) {
  if (!fileIds || !fileIds.length) return '';
  const rootId = getConfig_('DRIVE_ROOT_FOLDER_ID');
  const intakeRootId = getConfig_('INTAKE_UPLOAD_ROOT_ID');
  const root = DriveApp.getFolderById(intakeRootId);

  const today = new Date();
  const yyyy = today.getFullYear().toString();
  const mm = ('0'+(today.getMonth()+1)).slice(-2);
  const dd = ('0'+today.getDate()).slice(-2);

  const yearFolder = ensureChildFolder_(root, yyyy);
  const monthFolder = ensureChildFolder_(yearFolder, mm);
  const dayFolder = ensureChildFolder_(monthFolder, dd);
  const jobFolder = ensureChildFolder_(dayFolder, sanitizeFolderName_(jobNumber));
  const subFolder = ensureChildFolder_(jobFolder, sanitizeFolderName_(subcontractor));

  const links = [];
  fileIds.forEach(id => {
    try {
      const file = DriveApp.getFileById(id);
      // Move: add to target, remove from source parent(s)
      file.addToFolder(subFolder);
      const parents = file.getParents();
      while (parents.hasNext()) {
        const p = parents.next();
        if (p.getId() !== subFolder.getId()) {
          p.removeFile(file);
        }
      }
      links.push('https://drive.google.com/file/d/' + id + '/view');
    } catch (err) {
      links.push('ERROR:' + err);
    }
  });
  return links.join(', ');
}

function ensureChildFolder_(parent, name) {
  const it = parent.getFoldersByName(name);
  if (it.hasNext()) return it.next();
  return parent.createFolder(name);
}

function sanitizeFolderName_(s) {
  if (!s) return 'Unknown';
  return s.replace(/[\\/:*?"<>|#\[\]]/g, '-').trim();
}
