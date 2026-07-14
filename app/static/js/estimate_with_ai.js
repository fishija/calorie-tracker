document.getElementById('btn-ai-estimate').addEventListener('click', async function() {
  // Get the description and new photos input values
  const descriptionInput = document.getElementById('description');
  const newPhotosInput = document.getElementById('new_photos');
  const button = this;

  const dataUrl = this.getAttribute('data-url');

  // Create a FormData object to send the description and files
  const formData = new FormData();
  formData.append('description', descriptionInput.value);

  // Append each selected file to the FormData object
  if (newPhotosInput.files.length > 0) {
    for (let i = 0; i < newPhotosInput.files.length; i++) {
      formData.append('new_photos', newPhotosInput.files[i]);
    }
  }

  // Disable the button and show a loading state
  const originalText = button.innerHTML;
  button.disabled = true;
  button.innerHTML = 'Estimating...';

  try {
    // Send AJAX request to the server to get the estimation
    const response = await fetch(dataUrl, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to fetch estimation from AI.');
    }

    const data = await response.json();
    showEstimateModal(data);

  } catch (error) {
    alert('Error estimating macros: ' + error.message);
  } finally {
    button.disabled = false;
    button.innerHTML = originalText;
  }
});

function showEstimateModal(data) {
  // Populate modal fields
  document.getElementById('ai-calorie-kcal').textContent = data.calorie_kcal ?? '--';
  document.getElementById('ai-protein-g').textContent = data.protein_g ?? '--';
  document.getElementById('ai-carb-g').textContent = data.carb_g ?? '--';
  document.getElementById('ai-fat-g').textContent = data.fat_g ?? '--';

  const summaryEl = document.getElementById('ai-meal-summary');
  summaryEl.textContent = data.meal_summary || '';
  summaryEl.classList.toggle('d-none', !data.meal_summary);

  const confidenceWrap = document.getElementById('ai-confidence-wrap');
  const confidenceEl = document.getElementById('ai-confidence');
  if (data.confidence) {
    confidenceEl.textContent = data.confidence;
    confidenceEl.className = 'badge ' + confidenceBadgeClass(data.confidence);
    confidenceWrap.classList.remove('d-none');
  } else {
    confidenceWrap.classList.add('d-none');
  }

  const assumptionsWrap = document.getElementById('ai-assumptions-wrap');
  if (data.assumptions) {
    document.getElementById('ai-assumptions').textContent = data.assumptions;
    assumptionsWrap.classList.remove('d-none');
  } else {
    assumptionsWrap.classList.add('d-none');
  }

  // Wire up Accept — replace any previous listener to avoid stacking
  const acceptBtn = document.getElementById('btn-ai-accept');
  const newAcceptBtn = acceptBtn.cloneNode(true);
  acceptBtn.parentNode.replaceChild(newAcceptBtn, acceptBtn);

  newAcceptBtn.addEventListener('click', function() {
    document.getElementById('calorie_kcal').value = data.calorie_kcal || 0;
    document.getElementById('protein_g').value = data.protein_g || 0;
    document.getElementById('carb_g').value = data.carb_g || 0;
    document.getElementById('fat_g').value = data.fat_g || 0;
  });
  // Discard button just closes the modal via data-bs-dismiss, no listener needed

  const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('aiEstimateModal'));
  modal.show();
}

function confidenceBadgeClass(confidence) {
  switch ((confidence || '').toLowerCase()) {
    case 'high': return 'bg-success';
    case 'medium': return 'bg-warning text-dark';
    case 'low': return 'bg-danger';
    default: return 'bg-secondary';
  }
}