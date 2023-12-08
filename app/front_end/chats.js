/* Primary chat functions */
// -------------------------- Primary Backend Chat Functions -------------------------- //
// The first function will initialize the chat and set up the context, if any.
const initChat = (context, metadata, session_id) => {
  // Set up the chat thread with the context and metadata,
  // if any by sending it to the "./initialize-general-chat" route.
  // This will return a promise, which will be resolved with the
  // chat thread object.
  // If there is no metadata, set it to an empty object.
  metadata = metadata || {};
  return new Promise((resolve, reject) => {
    // Send the context and metadata to the server.
    $.ajax({
      url: "/initialize-general-chat",
      type: "POST",
      data: {
        message_content : context,
        metadata: metadata,
        session_id: session_id
      },
      success: (data) => {
        // Resolve the promise with the chat thread object.
        // Which includes the thread id, the sesssion id, and the message content
        resolve(data);
      },
      error: (err) => {
        // Reject the promise with the error.
        reject(err);
      }
    });
  });
}

// Create a send chat function that takes the user's input and passes it to the
// server to be processed.
const sendChat = (messageContent, threadId, sessionId, chefStyle, metadata) => {
  threadId = threadId || null;
  sessionId = sessionId || null;
  chefStyle = chefStyle || "home_cook"
  metadata = metadata || {};

  // Return a promise that will be resolved with the response from the server.
  return new Promise((resolve, reject) => {
    // Send the message content to the server.
    $.ajax({
      url: "/get-chef-response",
      type: "POST",
      data: {
        message_content: messageContent,
        thread_id: threadId,
        session_id: sessionId,
        chef_style: chefStyle
      },
      success: (data) => {
        // Resolve the promise with the response from the server.
        resolve(data);
      },
      error: (err) => {
        // Reject the promise with the error.
        reject(err);
      }
    });
  });
}

// Create a function to display the chat messages.
const displayChatMessage = (messageContent, messageSender) => {
  // Get the chat message container.
  const chatMessageContainer = document.getElementById("chatMessageContainer");
  // Create a new chat message element.
  const chatMessage = document.createElement("div");
  // Set the class name of the chat message element based on who sent it.
  chatMessage.className = messageSender === "user" ? "user-chat-message" : "chef-chat-message";
  // Set the text content of the chat message element.
  chatMessage.textContent = messageContent;
  // Append the chat message element to the chat message container.
  chatMessageContainer.appendChild(chatMessage);
}



  
  
