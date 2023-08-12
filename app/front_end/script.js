$(document).ready(function () {
    // Slide-up chat box
    $('#chat-box').slideDown();
    var sessionId = 'test12345'; // Replace with actual session ID if needed

    $('#send-btn').click(function () {
        var question = $('#user-input').val();
        $('#user-input').val('');

        // Fetch response from FastAPI
        $.ajax({
            url: `http://localhost:8000/get_chef_response?question=${question}&session_id=${sessionId}`,
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


