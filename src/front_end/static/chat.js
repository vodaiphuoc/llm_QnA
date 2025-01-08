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

/**
 * Get input from user and show it on screen on button click.
 */
$(document).ready(function(){
	$("#send_button").click(function() {
		// get and show message and reset input
		var paragraph_id = document.getElementsByClassName('paragraph_id')[0].innerHTML;
		var user_input_message = $('#msg_input').val();
		showUserMessage(user_input_message);
		$('#msg_input').val('');


		// send message to server
		let myHeaders = new Headers({
	        "Content-Type": "application/json",
	    });

	    fetch('/get_message', {
	        method: 'POST',
	        body: JSON.stringify({
	            para_id: paragraph_id,
	            user_message: user_input_message
	        }),
	        headers: myHeaders
	    })
	    .then((response)=>{
	        if (response.ok) {
	            response.text()
	            .then((message)=>{
	                console.log(message);
	                showBotMessage(message);
	            })
	            .catch((error)=>{
	                console.error('Failed to get model response', error);
	            });

	        } else {
	            throw new Error('response is not OK status');
	        }
	        
	    });

		// show bot message
		// setTimeout(function () {
		// 	showBotMessage(randomstring());
		// }, 300);

   });
 });


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