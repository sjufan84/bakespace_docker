function detectPageContext() {
    // Logic to detect the current page or context
    // Return a value that represents the context
  }
  
  function updateChatContent() {
    var context = detectPageContext();
    var contentWrapper = document.getElementById('chat-content-wrapper');
  
    // Clear existing content
    contentWrapper.innerHTML = '';
  
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
    document.getElementById('chat-box').style.display = 'block';
  }
  
  function closeChat() {
    document.getElementById('chat-box').style.display = 'none';
  }
  