<<<<<<< HEAD
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

=======
/*
	Chat Bot Functions
*/

function openChat() {
    $('#chat-bubble').hide();
    $('#chat-box').slideDown();
    $("#chat_history_div").animate({ scrollTop: $('#chat_history_div').height()+5000}, 1000);
    $('#chatMessageInput').focus();
}

$("#chatMessageInput").keypress(function (e) {
	if (e.which == 13) {
		$(".chat-send-btn").trigger("click");
	}
});

>>>>>>> 8527395785d28333fd5240a8229180810d928d69
function closeChat() {
    $('#chat-box').hide();
    $('#chat-bubble').show();
}
<<<<<<< HEAD
=======

$('#chatMessage').on('input', function() {
	this.style.height = 'auto';
	this.style.height = (this.scrollHeight) + 'px';
});

$('#doChatGeneral').on('click', function() {
	doChatCall('general', 0);
});

$('#doChatCookbook').on('click', function() {
	doChatCall('cookbook', $("#cookbookId").val() );
});

$('#doChatRecipe').on('click', function() {
	doChatCall('recipe', $("#recipeId").val() );
});

function doChatCall(type,id) {
	var msg = $("#chatMessageInput").val();
	var action = "";
	if (type=='recipe') {
		action = "doChatRecipe";
	}else if (type=='cookbook') {
		action = "doChatCookbook";
	}else if (type=='general') {
		action = "doChatGeneral";
	}else{
		action = "test";
	}
	$("#"+action).removeClass("chat-send-btn");
	$("#"+action).addClass("chat-send-btn-disabled");
	$("#"+action).prop("disabled", true);
	$.ajax({
		url: "/api/posts.php",
		data: {
			action: action,
			rid: id,
			msg: msg
		},
		method: "POST",
		success: function( data ) {
			$("#" + action).addClass("chat-send-btn");
			$("#" + action).removeClass("chat-send-btn-disabled");
			$("#" + action).prop("disabled", false);
			try { var o = JSON.parse(data); }
			catch (e) {
				alert("There was a problem with our chat engine.");
				return;
			}
			if (o.msg != "" && o.msg != null) {
				alert(o.msg);
				return;
			}
			if (o.session_id == null || o.session_id == "") {
				alert("There was a problem with our chat response.");
			}else{
				// success
				if (type=='recipe') {
					doChatPopulateRecipeCheck(id);
				}else if (type=='cookbook') {
					doChatPopulateCookbookCheck(id);
				}else if (type=='general') {
					doChatPopulateGeneralCheck(0);
				}
			}
		}
	});
}

function doChatPopulateRecipeCheck(rid){
	doChatPopulateCheck("doChatPopulateRecipeCheck", rid);
}
function doChatPopulateCookbookCheck(rid){
	doChatPopulateCheck("doChatPopulateCookbookCheck", rid);
}
function doChatPopulateGeneralCheck(rid){
	doChatPopulateCheck("doChatPopulateGeneralCheck", rid);
}

function doChatPopulateCheck(action,rid){
	$.ajax({
		url: "/api/posts.php",
		data: {
			action: action,
			rid: rid
		},
		method: "POST",
		success: function( data ) {
			try { var o = JSON.parse(data); }
			catch (e) {
				console.log("There was a problem with our chat engine.");
				return;
			}
			if (o.msg != "" && o.msg != null) {
				alert(o.msg);
				return;
			}
			if (o.chat_history_html != "" && o.chat_history_html != null) {
				//console.log(o.chat_history_html);
				$("#chat_history_div").html(o.chat_history_html);
				$("#chatMessageInput").val("");
				$("#chat_history_div").animate({ scrollTop: $('#chat_history_div').height()+5000 }, 1000);
				return;
			}
		}
	});
}
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
