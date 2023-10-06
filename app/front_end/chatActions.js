function bindSendButton(callback) {
    $('#send-btn').off('click').click(callback);
}

function getChefResponse() {
    // Existing AJAX code for getting a chef's response
}

function modifyRecipeAjax() {
    // AJAX code for modifying a recipe
}

function getPairingsAjax() {
    // AJAX code for getting pairings
}


function askQuestion() {
    $('#chat-content').html('<p>Type your question below and click Send.</p>');
    bindSendButton(getChefResponse); // Bind the send button to the appropriate function
}

function modifyRecipe() {
    $('#chat-content').html('<p>Type the modifications you want for the recipe below and click Send.</p>');
    $('#send-btn').off('click').click(function() {
        var question = $('#user-input').val();
        $('#user-input').val('');
        var sessionId = 'test-session-id'; // Replace with your session ID logic

        $.ajax({
            url: `http://localhost:8000/get_new_recipe?session_id=${sessionId}`,
            method: 'POST',
            data: { user_question: question },
            success: function(response) {
                // Handle the response, e.g., display the new recipe
                $('#chat-messages').append('<div>Sous Chef: ' + response.recipe_text + '</div>');
            }
        });
    });
    bindSendButton(modifyRecipeAjax); // Bind the send button to the appropriate function
}

function getPairings() {
    $('#chat-content').html('<p>Type the pairing type you want below and click Send.</p>');
    $('#send-btn').off('click').click(function() {
        var pairingType = $('#user-input').val();
        $('#user-input').val('');
        var sessionId = 'test-session-id'; // Replace with your session ID logic

        $.ajax({
            url: `http://localhost:8000/generate_pairing?session_id=${sessionId}`,
            method: 'POST',
            data: { pairing_type: pairingType },
            success: function(response) {
                // Handle the response, e.g., display the pairing recommendation
                $('#chat-messages').append('<div>Sous Chef: ' + response.pairing_text + '</div>');
            }
        });
    });
    bindSendButton(getPairingsAjax); // Bind the send button to the appropriate function
}

function surpriseMe() {
    $('#chat-content').html('<p>Surprise Me functionality coming soon!</p>');
    // Implement this function once the endpoint is available
}

$(document).ready(function () {
    // Show chat bubble initially
    $('#chat-bubble').show();
    var sessionId = 'test-session-id'; // Change this to your own session ID

    // Bind initial chat behavior
    askQuestion();
});