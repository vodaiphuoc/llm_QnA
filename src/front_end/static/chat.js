/**
 * Returns the current datetime for the message creation.
 */
function getCurrentTimestamp() {
	return new Date();
}

/**
 * Renders a message on the chat screen based on the given arguments.
 * This is called from the `showUserMessage` and `showBotMessage`.
 */
function renderMessageToScreen(args) {
	// local variables
	let displayDate = (getCurrentTimestamp()).toLocaleString('en-IN', {
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: 'numeric',
	});
	let messagesContainer = $('.messages');

	// init element
	let message = $(`
	<li class="message ${args.message_side}">
		<div class="avatar"></div>
		<div class="text_wrapper">
			<div class="text">${args.text}</div>
			<div class="timestamp">${displayDate}</div>
		</div>
	</li>
	`);

	// add to parent
	messagesContainer.append(message);

	// animations
	setTimeout(function () {
		message.addClass('appeared');
	}, 0);
	messagesContainer.animate({ scrollTop: messagesContainer.prop('scrollHeight') }, 300);
}


/**
 * Displays the user message on the chat screen. This is the right side message.
 */
function showUserMessage(message) {
	// render user input message
	renderMessageToScreen({
		text: message,
		message_side: 'right',
	});
}

/**
 * Displays the chatbot message on the chat screen. This is the left side message.
 */
function showBotMessage(message) {
	renderMessageToScreen({
		text: message,
		message_side: 'left',
	});
}


/* Sends a message when the 'Enter' key is pressed.
 */
$(document).ready(function() {
    $('#msg_input').keydown(function(e) {
        // Check for 'Enter' key
        if (e.key === 'Enter') {
            // Prevent default behaviour of enter key
            e.preventDefault();
			// Trigger send button click event
            $('#send_button').click();
        }
    });
});


function chatsession_callback() {
    /**
     * Callback function when history topic or `create_new_chat` are 
     * processes:
     *  (1) determine topic, if `create_new_chat`, topic is empty string
     *  (2) create new instance of websocket
     *  (3) listening to #send_button
     */

    // step (2)
    var ws = new WebSocket("ws://localhost:8080/ws");

    // step (3)
    $("#send_button").click(function() {
        var user_input_message = $('#msg_input').val();
        showUserMessage(user_input_message);
		$('#msg_input').val('');

        ws.send(JSON.stringify({
            topic: '',
            user_message: user_input_message
        }))
    })

    ws.addEventListener("message", (event) => {
        showBotMessage(event.data);
      });
}

/**
 * Assign event handler to `create_new_chat`
 */
$(document).ready(function(){
    $("#create_new_chat").on('click', chatsession_callback);

    
})





/**
 * Returns a random string. Just to specify bot message to the user.
 */
function randomstring(length = 20) {
	let output = '';

	// magic function
	var randomchar = function () {
		var n = Math.floor(Math.random() * 62);
		if (n < 10) return n;
		if (n < 36) return String.fromCharCode(n + 55);
		return String.fromCharCode(n + 61);
	};

	while (output.length < length) output += randomchar();
	return output;
}

/**
 * Set initial bot message to the screen for the user.
 */
$(window).on('load', function () {
	showBotMessage('Hello there! what u want to ask');
});