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

  var SLOT_LABELS = {
    asap: 'ASAP — earliest available',
    morning: 'Morning (8 AM – 11 AM)',
    afternoon: 'Afternoon (12 PM – 3 PM)',
    evening: 'Evening (4 PM – 7 PM)',
    night: 'Night (8 PM – 11 PM)'
  };

  ASTRAE.initTimeSlotPickers = function () {
    document.querySelectorAll('[data-time-slot-picker]').forEach(function (picker) {
      var input = picker.querySelector('[data-time-slot-input]');
      var cards = picker.querySelectorAll('.time-slot-card');
      var summary = picker.querySelector('[data-time-slot-summary]');
      var summaryText = picker.querySelector('[data-time-slot-summary-text]');
      var offerBadge = picker.closest('[data-offer-card]')
        ? picker.closest('[data-offer-card]').querySelector('[data-offer-schedule-badge]')
        : null;

      function updateSummary(code) {
        var label = SLOT_LABELS[code] || code;
        if (summary && summaryText) {
          summaryText.textContent = label;
          summary.classList.toggle('hidden', !code);
        }
        if (offerBadge) {
          var dateInput = picker.closest('form') && picker.closest('form').querySelector('[name="scheduled_date"]');
          var dateText = dateInput && dateInput.value ? dateInput.value : '';
          offerBadge.textContent = dateText && code
            ? dateText + ' · ' + label
            : (code ? label : 'Pick a date & time');
          offerBadge.classList.toggle('hidden', !code && !dateText);
        }
      }

      cards.forEach(function (card) {
        card.addEventListener('click', function () {
          var code = card.getAttribute('data-slot');
          input.value = code;
          cards.forEach(function (c) {
            var active = c === card;
            c.classList.toggle('active', active);
            c.setAttribute('aria-pressed', active ? 'true' : 'false');
          });
          updateSummary(code);
          input.dispatchEvent(new Event('change', { bubbles: true }));
        });
      });

      var dateInput = picker.closest('form') && picker.closest('form').querySelector('[name="scheduled_date"]');
      if (dateInput) {
        dateInput.addEventListener('change', function () {
          if (input.value) updateSummary(input.value);
          else if (offerBadge && dateInput.value) {
            offerBadge.textContent = dateInput.value + ' — select a time';
            offerBadge.classList.remove('hidden');
          }
        });
      }

      if (input.value) updateSummary(input.value);
    });
  };

  document.addEventListener('DOMContentLoaded', function () {
    ASTRAE.initFormLoading();
    ASTRAE.initTimeSlotPickers();
    if (document.querySelector('form[data-loading="compare"]')) {
      ASTRAE.initFormLoading();
    }
  });
})();
