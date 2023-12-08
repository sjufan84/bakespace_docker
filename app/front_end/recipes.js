// Recipe processing functions
import { sendChat, displayChatMessage } from './chats.js';

// Create a function to display the editable fields for the uploaded
// recipe.  Ingredients and directions fields should be a dropdown that
//let's the user select the ingredient and edit it in a text box if needed.
//The same should be done for the directions.
const displayAndEditRecipe = (recipe) => {
  console.log('displayAndEditRecipe called')
  // Parse the recipe if it's a string
  if (typeof recipe === 'string') {
    recipe = JSON.parse(recipe);
  }
  // Display the fields and values from the recipe in the recipeContent div
  let recipeContentDiv = document.getElementById('recipeContent');
  // Clear the current content
  recipeContentDiv.innerHTML = '';
  // Create a header
  let header = document.createElement('h4');
  header.innerHTML = 'Here are the details of the recipe you uploaded:';
  // Append the header to the recipeContent div
  recipeContentDiv.appendChild(header);
  // Create a div to hold the recipe details
  let recipeDetailsDiv = document.createElement('div');
  // Iterate over the fields in the recipe
  for (let field in recipe) {
    // Create a div to hold the field and value
    let fieldDiv = document.createElement('div');
    // Create a span for the field
    let fieldSpan = document.createElement('span');
    fieldSpan.className = 'font-bold';
    fieldSpan.innerHTML = `${field}: `;
    // Create a span for the value
    let valueSpan = document.createElement('span');
    valueSpan.innerHTML = recipe[field];
    // Append the field and value spans to the field div
    fieldDiv.appendChild(fieldSpan);
    fieldDiv.appendChild(valueSpan);
    // Append the field div to the recipe details div
    recipeDetailsDiv.appendChild(fieldDiv);
  }
    // Append the recipe details div to the recipeContent div
    recipeContentDiv.appendChild(recipeDetailsDiv);
    // Append a note to let the user know that they can ask BakeBot questions about the recipe
    // in the chat to the right
    let note = document.createElement('p');
    note.innerHTML = 'You can ask BakeBot questions about this recipe in the chat to the right!';
    // Append the note to the recipeContent div
    recipeContentDiv.appendChild(note);
    // Append a button to submit the recipe
    let submitButton = document.createElement('button');
    submitButton.className = 'btn btn-primary';
    submitButton.innerHTML = 'Submit Recipe';
    // Add an event listener to the submit button
    // If the user submits, we need to take all of the inputs
    // and pass them to the backend to be processed
    submitButton.addEventListener('click', () => {
      // Get the recipe name
      let recipeName = document.getElementById('recipeName').value;
      // Get the recipe ingredients
      let recipeIngredients = document.getElementById('recipeIngredients').value;
      // Get the recipe directions
      let recipeDirections = document.getElementById('recipeDirections').value;
      // Create a recipe object
      let recipe = {
        recipe_name: recipeName,
        recipe_ingredients: recipeIngredients,
        recipe_directions: recipeDirections
      };
      // Submit the recipe
      submitRecipe(recipe);
    });
}
// Create the submitRecipe function that takes the recipe object
// and passes it to the backend as a new message to the chat thread
// with the user
const submitRecipe = (recipe) => {
  messageContent, threadId, sessionId, chefStyle, metadata
  console.log('submitRecipe called with recipe:', recipe)
  // Pass the recipe object to the backend within a with the recipe object
  // as a mapping in the metadata
  let submitMessage = `The user has uploaded a recipe that they would like to ask questions about.  Here are the details: ${recipe}.`;
  let recipeMetadata = {
    "uploaded_recipe": recipe
  };
  console.log('recipeMetadata:', recipeMetadata)
  // Send the chat message to the backend and await the response
  sendChat(submitMessage, threadId, sessionId, chefStyle, recipeMetadata).then(response => {
    response = JSON.parse(response);
    console.log('response:', response.message)
    // Display BakeBot's response
    // Check to see if the response is in markdown
    if (response.message.includes('**')) {
      // Convert the markdown to HTML
      let html = converter.makeHtml(response.message);
      // Display the HTML
      displayChatMessage(html, 'bakebot');
    }
    else {
      // Display the response as text
      displayChatMessage(response.message, 'bakebot');
    }
    // Display the submitted recipe
    displaySubmittedRecipe(recipe);
  });
}

// Create a function to display the generated recipe
const displayRecipe = (recipeText) => {
  console.log('displayRecipe called')
  // Convert the recipe text to HTML
  let html = converter.makeHtml(recipeText);
  // Display the recipe text in the recipeContent div
  document.getElementById('recipeContent').innerHTML = html;
}


// Create a function to load in the local recipeData and then display the results in the 
// recipeContent div's innerHTML
const loadRecipeData = (recipeType) => {
  // If the recipeType is 'uploaded', then we need to display the editable fields
  // for the uploaded recipe
  if (recipeType === 'uploaded') {
    // Load the recipe data from the local storage
    let recipe = JSON.parse(localStorage.getItem('recipe'));
    // Display the editable recipe
    displayAndEditRecipe(recipe);
  }
  // If the recipeType is 'generated', then we need to display the generated recipe
  else if (recipeType === 'generated') {
    // Load the recipe data from the local storage
    let recipe = JSON.parse(localStorage.getItem('recipe'));
    // Display the generated recipe
    displayRecipe(recipe);
  }
}
