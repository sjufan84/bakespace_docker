import { displayMessage, sendChat } from './displayMessage.js';
import { saveRecipeToDatabase } from './saveRecipeToDatabase.js';

// -------------------------- Global Variables -------------------------- //
// Create a new showdown converter for converting markdown to HTML
const converter = new showdown.Converter();
let threadId = null;
let sessionId = null;
let messageMetadata = null;
let recipe = null;


  // Create a function to display the tool output
  const displayToolOutput = (tool, toolOutput, message) => {
    console.log('displayToolOutput called with tool:', tool, 'and message:', message, 'and toolOutput:', toolOutput)
    let toolName = tool.tool_name;
    // Get the tool name and output
    // If the tool name is generate_pairings, generate_image,
    // or adjust_recipe, display the message as HTML in the toolOutputs div
    if (toolName === 'generate_pairings' || toolName === 'generate_image') {
      // Convert the tool output to HTML
      console.log('toolOutput:', toolOutput)
      let html = converter.makeHtml(toolOutput);
      // Display the tool output in the toolOutputs div
      document.getElementById('toolOutputs').innerHTML = html;
      // Display the message in the chat
      displayMessage(html, 'bakebot');
    }
    
    // If the tool output is adjust_recipe, replaace the recipeContent div's innerHTML
    // with the new recipe content
    else if (toolName === 'adjust_recipe') {
      // Convert the tool output to HTML
      let html = converter.makeHtml(toolOutput);
      // Display the tool output in the recipeContent div
      document.getElementById('recipeContent').innerHTML = html;
      // Display the message in the chat
      displayMessage(html, 'bakebot');
    }
    // If the create recipe tool is called, replace the recipeContent div's innerHTML
    else if (toolName === 'create_recipe') {
      // Convert the tool output to HTML
      let html = converter.makeHtml(toolOutput);
      // Display the tool output in the recipeContent div
      document.getElementById('recipeContent').innerHTML = html;
    }
  }

  const saveRecipe = (recipe) => {
    // Save the recipe to the database
    // You'll need to replace this with your own function for saving the recipe
    // we coould also give this as a tool for the AI agent to use
    // @TODO: get token to test out database saves
    saveRecipeToDatabase(recipe);
  }

  const convertChefStyle = (chefStyle) => {
      const chefStyleMap = {
        'Classic Pro Chef': 'pro_chef',
        'Sweet Home Chef': 'home_cook',
        'Snarky Fun Chef': 'adventurous_chef'
      };
      return chefStyleMap[chefStyle] || chefStyle; // Fallback to original if not found
    }
  
  // Function to get the current value of the chef style dropdown
  const getChefStyle = () => {
    return document.getElementById('chefStyle').value;
  }
    
 // Event listener for the sendChat button
document.getElementById('sendChat').addEventListener('click', function() {
  console.log('sendChat clicked')
  // Show the spinner
  document.getElementById('spinner').style.display = 'inline-block';
  // Get the chef style from the dropdown
  let chefStyle = getChefStyle();
  // Convert the chef style to the backend's expected values
  chefStyle = convertChefStyle(chefStyle);
  // Get the user input
  let userInput = document.getElementById('chatInput').value;
  console.log('userInput:', userInput)
  // Check if the user input is empty
  if (userInput.trim() !== '') {
      // Display user question
      displayMessage(userInput, 'user');

      // Send the user input to the backend
      sendChat(userInput, threadId, sessionId, chefStyle, messageMetadata).then(response => {
          // Convert the response to a JavaScript object
          response = JSON.parse(response);
          // Extract the message from the response
          let message = response.message;
          // Extract the thread id from the response
          threadId = response.thread_id;
          // Extract the session id from the response
          sessionId = response.session_id;
          // Display the message
          displayMessage(message, 'bakebot');
          // Check to see if there is any tool output
          if (response.tool_return_values.length > 0) {
              // Handle each tool's output
              let tools = response.tool_return_values;
              tools.forEach(tool => {
                  // Convert the tool output to HMTL
                  let toolOutput = tool.tool_output;
                  displayToolOutput(tool, toolOutput, message);
              });
          }
          // Check to see if the user has asked to save the recipe
          if (message.includes('save recipe')) {
              // Save the recipe
              saveRecipe(recipe);
          }
          // Clear the input field
          document.getElementById('chatInput').value = '';
          // Hide the spinner
          document.getElementById('spinner').style.display = 'none';
      });
  }
  else {
      // Hide the spinner
      document.getElementById('spinner').style.display = 'none';
  }
});