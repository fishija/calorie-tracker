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

    // Update the form fields with the estimated values
    document.getElementById('calorie_kcal').value = data.calorie_kcal || 0;
    document.getElementById('protein_g').value = data.protein_g || 0;
    document.getElementById('carb_g').value = data.carb_g || 0;
    document.getElementById('fat_g').value = data.fat_g || 0;

    } catch (error) {
      alert('Error estimating macros: ' + error.message);
    } finally {
      button.disabled = false;
      button.innerHTML = originalText;
    }
});