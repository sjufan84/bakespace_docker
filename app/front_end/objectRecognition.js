// Function to display detected ingredients
function displayDetectedIngredients(ingredients) {
  const listElement = document.getElementById('detectedIngredientsList');
  listElement.innerHTML = ''; // Clear existing list
  ingredients.forEach(ingredient => {
      const listItem = document.createElement('li');
      listItem.className = 'list-group-item';
      listItem.textContent = ingredient;
      listElement.appendChild(listItem);
  });

  // Show the confirmation section
  document.getElementById('ingredientConfirmationSection').style.display = 'block';
  document.getElementById('recipeSpecificationsSection').style.display = 'block';
}

// Event listener for generating recipes
document.getElementById('generateRecipeButton').addEventListener('click', () => {
  const preferences = document.getElementById('recipePreferencesInput').value;
  // Call API to generate recipe with confirmed ingredients and preferences
});


