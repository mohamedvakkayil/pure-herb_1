(function () {
  'use strict';

  const modal = document.getElementById('record-modal');
  if (!modal) return;

  const backdrop = modal.querySelector('.modal-backdrop');
  const closeBtn = modal.querySelector('.modal-close');
  const cancelBtns = modal.querySelectorAll('.modal-cancel');
  const formSales = document.getElementById('form-sales');
  const formExpense = document.getElementById('form-expense');
  const modalActionsSales = document.getElementById('modal-actions-sales');
  const modalActionsExpense = document.getElementById('modal-actions-expense');
  const modalTitle = document.getElementById('modal-title');
  const modalErrors = document.getElementById('modal-errors');
  const salesForm = document.getElementById('sales-form');
  const expenseForm = document.getElementById('expense-form');

  let lastTrigger = null;

  function setTodayDate(formEl) {
    const dateInput = formEl.querySelector('input[type="date"]');
    if (dateInput) {
      const today = new Date().toISOString().split('T')[0];
      dateInput.value = today;
    }
  }

  function isVisible(el) {
    var node = el;
    while (node && node !== modal) {
      if (node.nodeType === 1 && window.getComputedStyle(node).display === 'none') return false;
      node = node.parentElement;
    }
    return true;
  }

  function getFocusableElements() {
    const selector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const elements = modal.querySelectorAll(selector);
    return Array.prototype.filter.call(elements, function (el) {
      return !el.disabled && el.getAttribute('tabindex') !== '-1' && isVisible(el);
    });
  }

  function setupFocusTrap() {
    modal.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab' || !modal.classList.contains('is-open')) return;
      const focusable = getFocusableElements();
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    });
  }

  function setupPaymentOptionClasses(form) {
    if (!form) return;
    const options = form.querySelectorAll('.payment-option');
    options.forEach(function (opt) {
      const input = opt.querySelector('input[type="radio"]');
      if (!input) return;
      opt.classList.toggle('is-selected', input.checked);
      input.addEventListener('change', function () {
        options.forEach(function (o) { o.classList.remove('is-selected'); });
        opt.classList.add('is-selected');
      });
    });
  }

  function openModal(type, trigger) {
    lastTrigger = trigger || null;
    formSales.style.display = type === 'sales' ? 'block' : 'none';
    formExpense.style.display = type === 'expense' ? 'block' : 'none';
    if (modalActionsSales) modalActionsSales.style.display = type === 'sales' ? 'flex' : 'none';
    if (modalActionsExpense) modalActionsExpense.style.display = type === 'expense' ? 'flex' : 'none';
    modalTitle.textContent = type === 'sales' ? 'Record Sale' : 'Record Expense';
    modalErrors.style.display = 'none';
    modalErrors.innerHTML = '';

    const form = type === 'sales' ? salesForm : expenseForm;
    if (form) {
      form.reset();
      setTodayDate(form);
      setupPaymentOptionClasses(form);
    }

    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    const firstInput = form && form.querySelector('input:not([type="hidden"]), textarea');
    if (firstInput) {
      setTimeout(function () { firstInput.focus(); }, 100);
    }
  }

  function closeModal() {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastTrigger) {
      lastTrigger.focus();
      lastTrigger = null;
    }
  }

  function showErrors(errors) {
    let html = '<ul>';
    for (const field in errors) {
      const msgs = Array.isArray(errors[field]) ? errors[field] : [errors[field]];
      msgs.forEach(function (msg) {
        html += '<li>' + escapeHtml(msg) + '</li>';
      });
    }
    html += '</ul>';
    modalErrors.innerHTML = html;
    modalErrors.style.display = 'block';
    modalErrors.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(function () {
      toast.classList.add('toast-out');
      setTimeout(function () { toast.remove(); }, 300);
    }, 2500);
  }

  function handleSubmit(e, url) {
    e.preventDefault();
    const form = e.target;
    if (!form.reportValidity()) return;

    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.textContent : '';

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Saving...';
    }
    modalErrors.style.display = 'none';
    modalErrors.innerHTML = '';

    fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json'
      },
      credentials: 'same-origin'
    })
      .then(function (res) {
        return res.json()
          .then(function (data) { return { ok: res.ok, data: data }; })
          .catch(function () { return { ok: false, data: { errors: { _: ['Invalid response from server.'] } } }; });
      })
      .then(function (_ref) {
        var ok = _ref.ok, data = _ref.data;
        if (ok && data.success) {
          closeModal();
          showToast('Record saved successfully.');
          window.location.reload();
        } else {
          if (data.errors) showErrors(data.errors);
        }
      })
      .catch(function () {
        showErrors({ _: ['Something went wrong. Please try again.'] });
      })
      .finally(function () {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
        }
      });
  }

  setupFocusTrap();

  document.querySelectorAll('[data-modal-type]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      openModal(btn.getAttribute('data-modal-type'), btn);
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', closeModal);
  cancelBtns.forEach(function (btn) { btn.addEventListener('click', closeModal); });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal.classList.contains('is-open')) {
      closeModal();
    }
  });

  if (salesForm) {
    salesForm.addEventListener('submit', function (e) {
      handleSubmit(e, salesForm.action);
    });
  }
  if (expenseForm) {
    expenseForm.addEventListener('submit', function (e) {
      handleSubmit(e, expenseForm.action);
    });
  }
})();
