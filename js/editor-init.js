// js/editor-init.js — minimal wiring to load uploaded files faithfully into the editor
// Depends on data/importers.js and the libs included in index.html (Mammoth, DOMPurify, Markdown-It)

import { importAnyToHtml } from '../data/importers.js';

(function initEditorWiring() {
  const input = document.getElementById('file');
  const output = document.getElementById('doc-content');
  const docMeta = document.getElementById('docMeta');
  const topMeta = document.getElementById('topMeta');
  const countMeta = document.getElementById('docCountMeta');

  if (!input || !output) {
    console.warn('[editor-init] Missing #file or #doc-content; skipping init.');
    return;
  }

  // If your Upload menu triggers #file.click() elsewhere, we just listen here.
  input.addEventListener('change', async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    // For now we load the first selected file into the editor.
    // (Your existing app.js may handle multiple—this won’t block it.)
    const file = files[0];

    try {
      setTopMeta(`Loading "${file.name}"…`);
      const html = await importAnyToHtml(file);

      // Inject HTML into the editable region faithfully.
      output.innerHTML = html;

      // Update simple meta labels if they exist
      if (docMeta) docMeta.textContent = [
        `Name: ${file.name}`,
        `Type: ${file.type || guessTypeFromExt(file.name)}`,
        `Size: ${formatBytes(file.size)}`
      ].join(' • ');

      if (topMeta) setTopMeta(`Loaded: ${file.name}`);
      if (countMeta) countMeta.textContent = 'Doc 1 of 1';

      // Focus the editor
      output.focus();

      // Ensure the canvas class is present (in case HTML already wrapped body)
      if (!output.querySelector('.doc-canvas')) {
        output.classList.add('doc-canvas');
      }

      // OPTIONAL HOOK: If your engine needs to rescan now, dispatch a custom event
      const event = new CustomEvent('lc:documentLoaded', { detail: { fileName: file.name }});
      document.dispatchEvent(event);

    } catch (err) {
      console.error('[editor-init] Import failed:', err);
      setTopMeta('Failed to load document. See console for details.');
      showToastInline('Could not load this document');
    } finally {
      // Reset the input so the same file can be selected again if needed
      input.value = '';
    }
  });

  // Tiny helpers (no external deps)
  function setTopMeta(msg) {
    if (topMeta) topMeta.textContent = msg;
  }
  function showToastInline(msg) {
    const err = document.getElementById('error');
    if (err) {
      err.textContent = msg;
      setTimeout(() => (err.textContent = ''), 3500);
    }
  }
  function formatBytes(bytes) {
    if (!+bytes) return '0 B';
    const units = ['B','KB','MB','GB'];
    const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
    }
  function guessTypeFromExt(name) {
    const ext = name.split('.').pop().toLowerCase();
    if (ext === 'docx') return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
    if (ext === 'html' || ext === 'htm') return 'text/html';
    if (ext === 'md' || ext === 'markdown') return 'text/markdown';
    if (ext === 'txt') return 'text/plain';
    return 'application/octet-stream';
  }
})();
