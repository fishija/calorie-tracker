document.addEventListener("DOMContentLoaded", function () {
  const wrapper = document.getElementById("goal-fields");
  if (!wrapper) return;

  const calorieInput = document.getElementById(wrapper.dataset.calorieId);
  const proteinInput = document.getElementById(wrapper.dataset.proteinId);
  const carbInput = document.getElementById(wrapper.dataset.carbId);
  const fatInput = document.getElementById(wrapper.dataset.fatId);

  const proteinPct = document.getElementById("protein_pct");
  const carbPct = document.getElementById("carb_pct");
  const fatPct = document.getElementById("fat_pct");
  const totalPct = document.getElementById("total_pct");

  // kcal per gram
  const KCAL_PER_G = { protein: 4, carb: 4, fat: 9 };

  function parseValue(input) {
    const raw = input.value.trim();
    if (raw === "") return null;
    const num = parseFloat(raw);
    return Number.isNaN(num) ? null : num;
  }

  function computePct(macroInput, pctOutput, kcalPerGram, calorieVal) {
    const macroVal = parseValue(macroInput);
    if (calorieVal === null || calorieVal === 0 || macroVal === null) {
      pctOutput.value = "-";
      return;
    }
    const pct = (macroVal * kcalPerGram * 100) / calorieVal;
    pctOutput.value = pct.toFixed(1) + "%";
  }

  const TOTAL_CLASSES = ["goal-total-input--empty", "goal-total-input--under", "goal-total-input--exact", "goal-total-input--over"];

  function setTotalClass(cls) {
    TOTAL_CLASSES.forEach(c => totalPct.classList.remove(c));
    totalPct.classList.add(cls);
  }

  function updateTotal(calorieVal) {
    const proteinVal = parseValue(proteinInput);
    const carbVal    = parseValue(carbInput);
    const fatVal     = parseValue(fatInput);

    if (proteinVal === null && carbVal === null && fatVal === null) {
      totalPct.value = "-";
      setTotalClass("goal-total-input--empty");
      return;
    }
    if (calorieVal === null || calorieVal === 0) {
      totalPct.value = "-";
      setTotalClass("goal-total-input--empty");
      return;
    }

    const sum = ((proteinVal ?? 0) * 4 + (carbVal ?? 0) * 4 + (fatVal ?? 0) * 9) / calorieVal * 100;
    totalPct.value = sum.toFixed(1) + "%";

    if (Math.abs(sum - 100) < 0.05) {
      setTotalClass("goal-total-input--exact");
    } else if (sum < 100) {
      setTotalClass("goal-total-input--under");
    } else {
      setTotalClass("goal-total-input--over");
    }
  }

  function updateAll() {
    const calorieVal = parseValue(calorieInput);
    computePct(proteinInput, proteinPct, KCAL_PER_G.protein, calorieVal);
    computePct(carbInput, carbPct, KCAL_PER_G.carb, calorieVal);
    computePct(fatInput, fatPct, KCAL_PER_G.fat, calorieVal);
    updateTotal(calorieVal);
  }

  [calorieInput, proteinInput, carbInput, fatInput].forEach((input) => {
    if (input) input.addEventListener("input", updateAll);
  });

  // initialize on load (handles pre-filled/edit case)
  updateAll();
});