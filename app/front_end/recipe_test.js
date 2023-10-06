// Load recipe by id
function loadRecipe(recipeId) {
    $.ajax({
      url: `http://bakespace.com/api/query.php?pcode=<partner_code>&type=recipe&id=${recipeId}`,
      method: 'GET',
      dataType: 'xml',
      success: function(response) {
        // Extract recipe details from the XML response
        var recipeName = $(response).find('name').text();
        var recipeText = $(response).find('directions').text();
  
        // Pass recipe text and question to API endpoint
        var question = $('#chatbox-input').val();
        var data = {
          recipeText: recipeText,
          question: question
        };
  
        $.ajax({
          url: 'https://api.example.com/process_question',
          method: 'POST',
          data: JSON.stringify(data),
          contentType: 'application/json',
          success: function(response) {
            // Handle the response from LLM
            var answer = response.answer;
            $('#chatbox-output').text(answer);
          },
          error: function() {
            console.error('Failed to process the question.');
          }
        });
      },
      error: function() {
        console.error('Failed to load the recipe.');
      }
    });
  }
  
  // Function to handle form submission
  function submitForm() {
    var recipeId = $('#recipe-id').val();
    loadRecipe(recipeId);
  }
  
  // Attach event listener to form submit button
  $('#recipe-form').on('submit', function(event) {
    event.preventDefault();
    submitForm();
  });
  ``