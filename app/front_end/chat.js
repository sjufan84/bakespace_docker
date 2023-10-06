function detectPageContext() {
    // Logic to detect the current page or context
    // Return a value that represents the context
}

function updateChatContent() {
    var context = detectPageContext();
    var contentWrapper = $('#chat-content-wrapper');

    // Clear existing content
    contentWrapper.html('');

    // Update content based on context
    if (context === 'recipePage') {
        // Example: Clone recipe options from main page
        var recipeOptions = $('#main-recipe-options').clone(true);
        contentWrapper.append(recipeOptions);
    } else if (context === 'homePage') {
        // Example: Add specific content for the home page
        contentWrapper.html('<p>Welcome to My Sous Chef!</p>');
    }
    // Add more conditions for different contexts
}

function openChat() {
    updateChatContent(); // Update content when chat is opened
    askQuestion(); // Default to "Ask a Question" option
    $('#chat-box').slideDown();
    $('#chat-bubble').hide();
}

function closeChat() {
    $('#chat-box').hide();
    $('#chat-bubble').show();
}
