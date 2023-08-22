function openChat() {
    $('#chat-bubble').hide();
    $('#chat-box').slideDown();
}

function closeChat() {
    $('#chat-box').hide();
    $('#chat-bubble').show();
}

$(document).ready(function () {
    // Show chat bubble initially
    $('#chat-bubble').show();
    var sessionId = 'test-session-id'; // Change this to your own session ID

    $('#send-btn').click(function () {
        // Existing AJAX code
        var question = $('#user-input').val(); // 
        $('#user-input').val('');

        // Fetch response from FastAPI
        $.ajax({
            url: `http://localhost:8000/get_chef_response?question=${question}&session_id=${sessionId}`, // Change this to your own server endpoint
            method: 'POST',
            success: function (response) {
                // Clear previous chat messages
                $('#chat-messages').empty();

                // Iterate through chat history and display messages
                var chatHistory = response.chat_history;
                chatHistory.forEach(function (chat) {
                    var role = chat.role === "system" ? "Sous Chef" : "User"; // Translate "system" role to "Sous Chef"
                    var content = chat.content;
                    $('#chat-messages').append('<div>' + role + ': ' + content + '</div>');
                });

                // Update session ID if needed
                sessionId = response.session_id;
            }
        });
    });
});


