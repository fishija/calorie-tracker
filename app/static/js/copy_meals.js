document.addEventListener("DOMContentLoaded", function () {
  initCopyToMode();
  initCopyFromMode();
});

function initCopyToMode() {
  const chipsWrap = document.getElementById('date_chips');
  if (!chipsWrap) return;

  const hiddenField = document.getElementById('to_dates_field');
  const hint = document.getElementById('chip_count_hint');
  const submitBtn = document.getElementById('to-submit-btn');
  const mealChecks = document.querySelectorAll('input[name="meal_ids"]');

  function currentDates() {
    return Array.from(chipsWrap.querySelectorAll('.date-chip'))
      .map(el => el.dataset.date)
      .filter(Boolean);
  }

  function sync() {
    const dates = currentDates();
    hiddenField.value = dates.join(',');
    const anyMealChecked = Array.from(mealChecks).some(c => c.checked);
    // submitBtn.disabled = !(dates.length > 0 && anyMealChecked);
    hint.textContent = dates.length === 0
      ? 'No dates selected yet.'
      : dates.length + ' day' + (dates.length > 1 ? 's' : '') + ' selected.';
  }

  function addChip(dateStr) {
    if (!dateStr || currentDates().includes(dateStr)) return;
    const chip = document.createElement('span');
    chip.className = 'date-chip';
    chip.dataset.date = dateStr;
    chip.innerHTML = dateStr + ' <button type="button" class="btn-close btn-close-chip" aria-label="Remove date" style="font-size:.6rem;"></button>';
    chipsWrap.appendChild(chip);
    sync();
  }

  chipsWrap.addEventListener('click', function (e) {
    if (e.target.classList.contains('btn-close-chip')) {
      e.target.closest('.date-chip').remove();
      sync();
    }
  });

  document.getElementById('add_date_btn').addEventListener('click', function () {
    const input = document.getElementById('add_date');
    addChip(input.value);
    input.value = '';
  });

  document.getElementById('add_range_btn').addEventListener('click', function () {
    const start = document.getElementById('range_start').value;
    const end = document.getElementById('range_end').value;
    if (!start || !end) return;
    let cur = new Date(start);
    const last = new Date(end);
    if (cur > last) return;
    while (cur <= last) {
      addChip(cur.toISOString().slice(0, 10));
      cur.setDate(cur.getDate() + 1);
    }
  });

  mealChecks.forEach(c => c.addEventListener('change', sync));
  sync();
}

function initCopyFromMode() {
  const submitBtn = document.getElementById('from-submit-btn');
  if (!submitBtn) return;

  const mealChecks = document.querySelectorAll('input[name="meal_ids"]');
  mealChecks.forEach(c => c.addEventListener('change', function () {}));
}
