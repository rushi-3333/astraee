/** ASTRAE UI utilities — loading states, tabs, form submit feedback */
(function () {
  'use strict';

  window.ASTRAE = window.ASTRAE || {};

  ASTRAE.showLoading = function (message) {
    var el = document.getElementById('astrae-loading');
    if (!el) {
      el = document.createElement('div');
      el.id = 'astrae-loading';
      el.className = 'loading-overlay';
      el.innerHTML = '<div class="loading-spinner"></div><p class="mt-4 text-sm font-medium text-slate-600" id="astrae-loading-msg"></p>';
      document.body.appendChild(el);
    }
    document.getElementById('astrae-loading-msg').textContent = message || 'Loading...';
    el.style.display = 'flex';
  };

  ASTRAE.hideLoading = function () {
    var el = document.getElementById('astrae-loading');
    if (el) el.style.display = 'none';
  };

  ASTRAE.initFormLoading = function () {
    document.querySelectorAll('form[data-loading]').forEach(function (form) {
      form.addEventListener('submit', function () {
        ASTRAE.showLoading(form.getAttribute('data-loading') || 'Processing...');
      });
    });
  };

  ASTRAE.initTabs = function (groupId, onSelect) {
    var btns = document.querySelectorAll('[data-tab-group="' + groupId + '"]');
    btns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var tab = btn.getAttribute('data-tab');
        btns.forEach(function (b) { b.setAttribute('aria-selected', b === btn ? 'true' : 'false'); });
        document.querySelectorAll('[data-tab-panel="' + groupId + '"]').forEach(function (p) {
          p.classList.toggle('hidden', p.getAttribute('data-tab') !== tab);
        });
        if (onSelect) onSelect(tab);
      });
    });
  };

  document.addEventListener('DOMContentLoaded', function () {
    ASTRAE.initFormLoading();
    if (document.querySelector('form[data-loading="compare"]')) {
      ASTRAE.initFormLoading();
    }
  });
})();
