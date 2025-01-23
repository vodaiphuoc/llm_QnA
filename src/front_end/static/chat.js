const topic_icon = '<i class="bi bi-chat-left-dots">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</i>';

function display_chat_history(topic_value) {
    /**
     * Given `topic_value` of clicked `tag_id` element, send post request to server
     * and render old history chat
     * Args:
     *  - topic_value (str)
     */

    fetch('/load_history', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            topic_value: topic_value
        })
    })
    .then((response)=> {
        if (response.ok) {
            response.json()
            .then((chat_history)=>{
                for (i = 0; i < chat_history.length; i++) {
                    showMessageByRole(
                        chat_history[i]['parts'],
                        chat_history[i]['role'],
                        chat_history[i]['timestamp']
                    );
                }
            });
        } else {
            console.log('error loading old messages');
        }
        
    });

}

function chatsession_callback() {
    /**
     * Callback function when history topic or `create_new_chat` are 
     * processes:
     *  (1) determine topic, if `create_new_chat`, topic is empty string
     *  (2) render chat history of current topic
     *  (3) create new instance of websocket
     *  (4) add listener to #send_button for sending msgs
     *  (5) listening on `message` event of websocket
     */

    console.log('check topic: ', this.id, $(`#${this.id}`).text());

    // step (1)
    let topic_value = ''
    if (this.id === 'create_new_chat') {
        topic_value = ''
    } else {
        topic_value = $(`#${this.id}`).text();
        // step (2)
        display_chat_history(topic_value);
    }

    // step (3)
    var ws = new WebSocket("ws://localhost:8080/ws");

    
    $("#send_button").click(function() {

        console.log('send button, check topic_value: ', topic_value);

        // step (4)
        var user_input_message = $('#msg_input').val();
        let user_timestamp = displayDate = (getCurrentTimestamp()).toLocaleString('en-IN', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
        });
        showMessageByRole(user_input_message, 'user',user_timestamp);
		$('#msg_input').val('');

        ws.send(JSON.stringify({
            topic: topic_value,
            user_message: user_input_message,
            time_stamp: user_timestamp
        }));
    });

    ws.addEventListener("message", (event) => {
        let processed_data = JSON.parse(event.data);
        
        // display new message
        showMessageByRole(processed_data['msg'], 'agent');

        console.log('check agent reponse: ',processed_data);
        
        // key `topic` only appear when `new_chat` is created
        if ('topic' in processed_data) {

            console.log('check length of all topics: ', $("[id^=topic_]").length);

            let new_id = $("[id^=topic_]").length;
            $("#all_topics").append(`<li id="topic_${new_id}">${topic_icon}${processed_data['topic']}</li>`);

            topic_value = processed_data['topic'];
        }



    });
}


function load_topics() {
    /**
     * Load all topics when start papges
     */

    fetch('/load_topics', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            'user': 'user'
        })
    })
    .then((response)=> {
        if (response.ok) {
            response.json()
            .then((response_topics)=>{

                for (i = 0; i < response_topics.length; i++) {
                    // append topic elements to `all_topics`
                    $("#all_topics").append(`<li id="topic_${i}">${topic_icon}${response_topics[i]}</li>`)
                    
                    // assign click handler
                    $(`li#topic_${i}`).on("click", chatsession_callback);
                }
            });
        } else {
            console.log('error loading topics');
        }
        
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
 * Assign event handler to `create_new_chat`
 */
$(document).ready(function(){
    load_topics();

    $("#create_new_chat").on('click', chatsession_callback);

    
})

