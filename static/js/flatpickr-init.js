document.addEventListener('DOMContentLoaded', function() {
  var els = document.querySelectorAll('.flatpickr-date, input[data-flatpickr]');
  if (els.length === 0) return;
  els.forEach(function(el) {
    flatpickr(el, {
      dateFormat: 'Y-m-d',
      allowInput: false,
      disableMobile: true
    });
  });
});
