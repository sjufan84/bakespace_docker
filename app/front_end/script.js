var currentAction = 'askQuestion'; // Global variable to store the current action

function handleSendButton() {
    var sessionId = 'test-session-id'; // Replace with your session ID logic
    var userInput = $('#user-input').val();
    $('#user-input').val('');

    var url, data;
    switch (currentAction) {
        case 'askQuestion':
            url = `http://localhost:8000/get_chef_response?question=${userInput}&session_id=${sessionId}`;
            break;
        case 'modifyRecipe':
            url = `http://localhost:8000/get_new_recipe?session_id=${sessionId}`;
            data = { user_question: userInput };
            break;
        case 'getPairings':
            url = `http://localhost:8000/generate_pairing?session_id=${sessionId}`;
            data = { pairing_type: userInput };
            break;
        // Add other cases if needed
    }

    $.ajax({
        url: url,
        method: 'POST',
        data: data,
        success: function (response) {
            // Handle the response based on the current action
            // ...
        }
    });
}

function askQuestion() {
    currentAction = 'askQuestion';
    $('#chat-content').html('<p>Type your question below and click Send.</p>');
}

function modifyRecipe() {
    currentAction = 'modifyRecipe';
    $('#chat-content').html('<p>Type the modifications you want for the recipe below and click Send.</p>');
}

function getPairings() {
    currentAction = 'getPairings';
    $('#chat-content').html('<p>Type the pairing type you want below and click Send.</p>');
}

function detectPageContext() {
    // Logic to detect the current page or context
    // Return a value that represents the context
  }
  
function updateChatContent() {
var context = detectPageContext();
var contentWrapper = $('#chat-content-wrapper'); // Changed to jQuery for consistency

// Clear existing content
contentWrapper.html('');

// Update content based on context
if (context === 'recipePage') {
    // Example: Clone recipe options from main page
    var recipeOptions = document.getElementById('main-recipe-options').cloneNode(true);
    contentWrapper.appendChild(recipeOptions);
} else if (context === 'homePage') {
    // Example: Add specific content for the home page
    contentWrapper.innerHTML = '<p>Welcome to My Sous Chef!</p>';
}
// Add more conditions for different contexts
}
  
function openChat() {
    updateChatContent(); // Update content when chat is opened
    askQuestion(); // Default to "Ask a Question" option
    $('#chat-box').slideDown(); // Changed to jQuery for consistency
    $('#chat-bubble').hide();
}
  
function closeChat() {
    $('#chat-box').hide(); // Changed to jQuery for consistency
    $('#chat-bubble').show();
}

$(document).ready(function () {
    // Show chat bubble initially
    $('#chat-bubble').show();
    $('#send-btn').click(handleSendButton); // Use the new handler function
});