let funFacts = [];

// Function to fetch and parse the CSV file
function loadFunFacts() {
    fetch('../../resources/cooking_fun_facts.csv')
        .then(response => response.text())
        .then(text => {
            const lines = text.split('\n');
            // Skip the header, start from line 1
            for (let i = 1; i < lines.length; i++) {
                if (lines[i].trim() !== '') {
                    funFacts.push(lines[i].trim());
                }
            }
        });
}

// Call this function when your app loads
loadFunFacts();

// Function to handle chef style button clicks
document.querySelectorAll('#chefStyleButtons').forEach(button => {
    button.addEventListener('click', function() {
        // Remove highlighting from all chef style buttons
        document.querySelectorAll('#chefStyleButtons').forEach(btn => btn.classList.remove('btn-secondary'));
        // Highlight the selected button
        this.classList.add('btn-secondary');
        // Store the selected chef style
        document.chefStyle = this.value;
    });
});

// Function to handle serving size button clicks
document.querySelectorAll('#servingSizeButtons').forEach(button => {
    button.addEventListener('click', function() {
        // Remove highlighting from all serving size buttons
        document.querySelectorAll('#servingSizeButtons').forEach(btn => btn.classList.remove('btn-secondary'));
        // Highlight the selected button
        this.classList.add('btn-secondary');
        // Store the selected serving size
        document.servingSize = this.value;
    });
});

document.getElementById('askBakeBot').addEventListener('click', function() {
  let question = document.getElementById('userQuestion').value;
  let chefStyle = document.chefStyle; // Use the stored chef style
  let servingSize = document.servingSize; // Use the stored serving size

  // Convert the frontend chef style to match the backend model's expected values
  let chefType;
  if (chefStyle === "Home Cook") {
      chefType = "home_cook";
  }
  else if (chefStyle === "Pro Chef") {
      chefType = "pro_chef";
  }
  else {
      chefType = "adventurous_chef";
  }
  message_content = question + " " + "Serving Size: " + servingSize + " "
  console.log(JSON.stringify({
          "message_content": question,
          "chef_type": chefType, // Ensure this matches 'chef_type' in the Pydantic model
          "serving_size": servingSize
      }));
    // Hide the button
    this.style.display = 'none';

  // Show and start fun facts
  startFunFacts();
  // Show the spinner
  document.getElementById('bbSpinner').style.display = 'block';

  // Send this data to FastAPI backend
  fetch('http://localhost:8000/create_thread_run', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          "message_content": question,
          "chef_type": chefType, // Ensure this matches 'chef_type' in the Pydantic model
          "serving_size": servingSize
      })
  }
  ).then(response => response.json())
  .then(data => {
    localStorage.setItem('recipeData', data);
    localStorage.setItem('recipeType', 'new')
    // Redirect to the display page with the token as a query parameter
    window.location.href = `display.html`;
    // Hide the spinner
    document.getElementById('bbSpinner').style.display = 'none';
  })
  .catch(error => console.error('Error:', error))
  .finally(() => {
    // Stop fun facts
    stopFunFacts();
    document.getElementById('bbSpinner').style.display = 'none';
  });
});

document.getElementById('uploadButton').addEventListener('click', function() {
console.log("upload button clicked");
// If the recipe is in the text area, add it to the form data
let recipeText = document.getElementById('userQuestion').value;
if (recipeText.trim() !== '') {
    let formData = new FormData();
    formData.append('recipe_text', recipeText);
    // Send the recipe text to the backend
    fetch('http://localhost:8000/format-recipe', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
      // Update the uploadedRecipeData variable
      localStorage.setItem('recipeData', data);
      localStorage.setItem('recipeType', 'uploaded');
      console.log(data);
      // Redirect to the display page with the token as a query parameter
      window.location.href = `display.html`;
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
      // Stop fun facts
      stopFunFacts();
      document.getElementById('bbSpinner').style.display = 'none';
    });
    // If there are files instead of text, add them to the form data
} else if (document.getElementById('formFileMultiple').files.length > 0) {
    let formData = new FormData();
    for (let i = 0; i < document.getElementById('formFileMultiple').files.length; i++) {
        formData.append('files', document.getElementById('formFileMultiple').files[i]);
    }
    // Send the files to the backend
    fetch('http://localhost:8000/upload-files/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
      // Update the uploadedRecipeData variable
      localStorage.setItem('recipeData', data);
      localStorage.setItem('recipeType', 'uploaded');
      console.log(data);
      // Redirect to the display page with the token as a query parameter
      window.location.href = `display.html`;
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
      // Stop fun facts
      stopFunFacts();
      document.getElementById('bbSpinner').style.display = 'none';
    });
  }
});

let funFactInterval;
let currentFactIndex = 0;

function startFunFacts() {
    // Show fun facts container
    const funFactsContainer = document.getElementById('funFactsContainer');
    funFactsContainer.style.display = 'block';

    // Start cycling through fun facts
    funFactInterval = setInterval(() => {
        if (funFacts.length > 0) {
            currentFactIndex = Math.floor(Math.random() * funFacts.length);
            funFactsContainer.textContent = funFacts[currentFactIndex];
        }
    }, 6000); // Change fun fact every 3 seconds
}

function stopFunFacts() {
    clearInterval(funFactInterval);
    document.getElementById('funFactsContainer').style.display = 'none';
    // Show the button again
    document.getElementById('askBakeBot').style.display = 'block';
    document.getElementById('uploadButton').style.display = 'block';
}
