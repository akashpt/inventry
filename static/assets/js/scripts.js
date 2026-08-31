document.addEventListener('DOMContentLoaded', function () {
  initDropZones();
  initDynamicRowButtons();
  initQuickCreateDropdown();
  initSearchFields();
  initButtonActions();
  initPlaceholderLinks();
});

function initDropZones() {
  document.querySelectorAll('.drop-zone').forEach(function (zone) {
    zone.addEventListener('click', function () {
      const input = zone.querySelector('input[type=file]');
      if (input) input.click();
    });
    zone.addEventListener('dragover', function (event) {
      event.preventDefault();
      zone.classList.add('dragover');
    });
    zone.addEventListener('dragleave', function () {
      zone.classList.remove('dragover');
    });
    zone.addEventListener('drop', function (event) {
      event.preventDefault();
      zone.classList.remove('dragover');
      const files = Array.from(event.dataTransfer.files).slice(0, 10);
      const status = zone.querySelector('.drop-zone-status');
      if (status) {
        status.textContent = files.map((file) => file.name).join(', ') || 'No file selected yet.';
      }
    });
    const input = zone.querySelector('input[type=file]');
    if (input) {
      input.addEventListener('change', function () {
        const files = Array.from(input.files).slice(0, 10);
        const status = zone.querySelector('.drop-zone-status');
        if (status) {
          status.textContent = files.map((file) => file.name).join(', ') || 'No file selected yet.';
        }
      });
    }
  });
}

function initDynamicRowButtons() {
  document.querySelectorAll('[data-add-row]').forEach(function (button) {
    button.addEventListener('click', function () {
      const target = document.querySelector(button.dataset.addRow);
      if (!target) return;
      const template = target.querySelector('tr.template-row');
      if (!template) return;
      const clone = template.cloneNode(true);
      clone.classList.remove('d-none', 'template-row');
      clone.querySelectorAll('input, select').forEach(function (control) {
        if (control.type === 'text' || control.type === 'number') control.value = '';
        if (control.tagName.toLowerCase() === 'select') control.selectedIndex = 0;
      });
      target.querySelector('tbody').appendChild(clone);
      showToast('New row added.');
    });
  });
}

function initQuickCreateDropdown() {
  const menu = document.querySelector('#quickCreateMenu');
  if (!menu) return;
  menu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      const href = link.getAttribute('href');
      if (href) {
        window.location.href = href;
      }
    });
  });
}

function initSearchFields() {
  document.querySelectorAll('input[type="search"], input[placeholder^="Search"]').forEach(function (input) {
    input.addEventListener('input', function () {
      const table = findNearestTable(input);
      if (!table) return;
      filterTable(table, input.value);
    });
  });
}

function initButtonActions() {
  document.addEventListener('click', function (event) {
    const button = event.target.closest('button, a.btn, a.text-reset');
    if (!button || shouldSkipButton(button)) return;

    const label = controlLabel(button);
    if (button.dataset.saveRedirect) {
      event.preventDefault();
      saveAndGo(button.dataset.saveMessage || 'Saved.', button.dataset.saveRedirect);
      return;
    }

    if (label.includes('new expense') || label === 'add expense') {
      event.preventDefault();
      addExpenseRow();
      return;
    }

    if (label === 'save item') {
      event.preventDefault();
      saveAndGo('Item saved.', '/products');
      return;
    }

    if (label === 'save quote') {
      event.preventDefault();
      saveAndGo('Quote saved.', '/invoice');
      return;
    }

    if (label === 'convert to invoice') {
      event.preventDefault();
      saveAndGo('Quote converted.', '/invoice');
      return;
    }

    if (label === 'save as paid') {
      event.preventDefault();
      markPayment('Paid');
      return;
    }

    if (label === 'save as draft') {
      event.preventDefault();
      markPayment('Draft');
      return;
    }

    if (label === 'export') {
      event.preventDefault();
      exportNearestTable(button);
      return;
    }

    if (label === 'filter') {
      event.preventDefault();
      applyVisibleFilters(button);
      return;
    }

    if (label === 'sort' || label.includes('sort by name')) {
      event.preventDefault();
      sortNearestTable(button);
      return;
    }

    if (label === 'scan') {
      event.preventDefault();
      fillBarcode(button);
      return;
    }

    if (label === 'clear applied amount') {
      event.preventDefault();
      clearAppliedAmounts(button);
      return;
    }

    if (label === 'more' || label === 'date range' || label === 'bulk actions') {
      event.preventDefault();
      showToast(actionMessage(label));
    }
  });
}

function initPlaceholderLinks() {
  document.querySelectorAll('a[href="#"]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      if (event.defaultPrevented) return;

      const label = controlLabel(link);
      if (label === 'home') {
        event.preventDefault();
        window.location.href = '/';
        return;
      }

      event.preventDefault();
      showToast(actionMessage(label));
    });
  });
}

function shouldSkipButton(button) {
  return button.matches('[data-bs-toggle], .btn-close, .dropdown-toggle, .nav-link, [data-add-row]');
}

function currentPage() {
  const page = window.location.pathname.split('/').pop();
  return page || 'index';
}

function normalizeText(text) {
  return text.replace(/\s+/g, ' ').trim().toLowerCase();
}

function controlLabel(element) {
  return normalizeText(element.textContent || element.getAttribute('aria-label') || '');
}

function findNearestTable(element) {
  const section = element.closest('.section-card, .container-fluid, body');
  return section ? section.querySelector('table') : null;
}

function filterTable(table, query) {
  const value = query.trim().toLowerCase();
  table.querySelectorAll('tbody tr:not(.template-row)').forEach(function (row) {
    row.classList.toggle('d-none', value && !row.textContent.toLowerCase().includes(value));
  });
}

function applyVisibleFilters(button) {
  const section = button.closest('.container-fluid') || document;
  const select = section.querySelector('.section-card select');
  const table = section.querySelector('table');

  if (!select || !table) {
    showToast('Filter options are ready on this page.');
    return;
  }

  const value = normalizeText(select.value);
  if (value.startsWith('all')) {
    filterTable(table, '');
    showToast('Showing all records.');
    return;
  }

  table.querySelectorAll('tbody tr:not(.template-row)').forEach(function (row) {
    row.classList.toggle('d-none', !normalizeText(row.textContent).includes(value));
  });
  showToast('Filter applied.');
}

function sortNearestTable(button) {
  const table = findNearestTable(button);
  if (!table) {
    showToast('Nothing to sort on this page.');
    return;
  }

  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr:not(.template-row)'));
  const sortIndex = table.id === 'quoteItemsTable' ? 0 : 1;
  const direction = table.dataset.sortDirection === 'asc' ? 'desc' : 'asc';

  rows.sort(function (a, b) {
    const first = cellValue(a, sortIndex);
    const second = cellValue(b, sortIndex);
    return direction === 'asc' ? first.localeCompare(second) : second.localeCompare(first);
  });

  rows.forEach(function (row) {
    tbody.appendChild(row);
  });
  table.dataset.sortDirection = direction;
  showToast('Table sorted ' + direction + '.');
}

function cellValue(row, index) {
  const cell = row.children[index] || row.children[0];
  const input = cell.querySelector('input, select');
  return normalizeText(input ? input.value : cell.textContent);
}

function exportNearestTable(button) {
  const table = findNearestTable(button) || document.querySelector('table');
  if (!table) {
    showToast('No table found to export.');
    return;
  }

  const rows = Array.from(table.querySelectorAll('tr:not(.template-row)')).filter(function (row) {
    return !row.classList.contains('d-none');
  });
  const csv = rows.map(function (row) {
    return Array.from(row.children).map(function (cell) {
      const input = cell.querySelector('input, select');
      const value = input ? input.value : cell.textContent;
      return '"' + value.trim().replace(/"/g, '""') + '"';
    }).join(',');
  }).join('\n');

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = currentPage() + '-export.csv';
  link.click();
  URL.revokeObjectURL(link.href);
  showToast('Export downloaded.');
}

function saveAndGo(message, href) {
  showToast(message);
  setTimeout(function () {
    window.location.href = href;
  }, 650);
}

function markPayment(status) {
  document.querySelectorAll('.badge').forEach(function (badge) {
    if (normalizeText(badge.textContent) === 'pending' || normalizeText(badge.textContent) === 'draft') {
      badge.textContent = status;
      badge.className = status === 'Paid' ? 'badge badge-paid' : 'badge badge-draft';
    }
  });
  showToast('Payment saved as ' + status.toLowerCase() + '.');
}

function clearAppliedAmounts(button) {
  const section = button.closest('.section-card') || document;
  section.querySelectorAll('input[type="number"]').forEach(function (input) {
    input.value = '';
  });
  showToast('Applied amounts cleared.');
}

function fillBarcode(button) {
  const group = button.closest('.input-group');
  const input = group ? group.querySelector('input') : null;
  if (input) {
    input.value = '6281002026088';
    input.focus();
  }
  showToast('Barcode scanned.');
}

function addExpenseRow() {
  const tbody = document.querySelector('tbody');
  if (!tbody) return;

  const row = document.createElement('tr');
  row.innerHTML = '<td>Aug 8, 2026</td><td>New Expense</td><td>New expense entry</td><td>Vendor</td><td class="text-end">AED 0.00</td><td>Cash</td>';
  tbody.prepend(row);
  showToast('Expense row added.');
}

function actionMessage(label) {
  const messages = {
    'notifications': 'No new notifications.',
    'more': 'More actions are available from the row actions.',
    'date range': 'Date range picker is ready to connect.',
    'bulk actions': 'Select rows to use bulk actions.'
  };

  return messages[label] || 'Action completed.';
}

function showToast(message) {
  let toast = document.querySelector('.app-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'app-toast';
    toast.setAttribute('role', 'status');
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(function () {
    toast.classList.remove('show');
  }, 2200);
}
