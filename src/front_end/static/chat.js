function display_chat_history(topic_value) {
    /**
     * Given `topic_value` of clicked `tag_id` element, send post request to server
     * and render old history chat
     */

    // let myHeaders = new Headers({
    //     "Content-Type": "application/json",
    // });

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
            .then((data)=>{
                
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
     *  (5) listening to #send_button
     */

    
    // step (1)
    let topic_value = ''
    if (this.id === 'create_new_chat') {
        topic_value = ''
    } else {
        topic_value = $(`#${this.id}`).text();
    }

    // step (2)
    display_chat_history(topic_value)

    // step (3)
    var ws = new WebSocket("ws://localhost:8080/ws");

    // step (4)
    $("#send_button").click(function() {
        var user_input_message = $('#msg_input').val();
        showMessageByRole(user_input_message, 'user');
		$('#msg_input').val('');

        ws.send(JSON.stringify({
            topic: topic_value,
            user_message: user_input_message
        }))
    })

    ws.addEventListener("message", (event) => {
        let processed_data = JSON.parse(event.data);
        
        // display new message
        showMessageByRole(processed_data['msg'], 'agent');
        
        // key `topic` only appear when `new_chat` is created
        if ('topic' in processed_data) {
            let new_id = $("#all_topics").length;
            $("#all_topics").append(`<li id="topic_${new_id}">${processed_data['topic']}</li>`);
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
                    $("#all_topics").append(`<li id="topic_${i}">${response_topics[i]}</li>`)
                    
                    // assign click handler
                    console.log('check li: ',$(`#topic_${i}`));
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

