$(document).ready(function () {
//links
//http://eloquentjavascript.net/09_regexp.html
//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions


    var messages = [], //array that hold the record of each string in chat
        lastUserMessage = "", //keeps track of the most recent input string from the user
        botMessage = "", //var keeps track of what the chatbot is going to say
        botName = 'Zephyr', //name of the chatbot
        user = 'User',
        session_id = '',
        talking = false; //when false the speach function doesn't work


    console.log("HEREE");
    var sessionInput = document.getElementById("session_id");
    if (sessionInput !== null) {
        var sessionID = sessionInput.value;
        session_id = sessionID;
        console.log(session_id);
    } else {
        console.log("session_id input element not found");
    }
//
//
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//edit this function to change what the chatbot says
    function chatbotResponse() {
        talking = true;
        botMessage = "I'm confused"; //the default message

        if (lastUserMessage === 'hi' || lastUserMessage =='hello') {
            const hi = ['hi','howdy','hello']
            botMessage = hi[Math.floor(Math.random()*(hi.length))];;
        }

        if (lastUserMessage === 'name') {
            botMessage = 'My name is ' + botName;
        }
    }
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//
//
//
//this runs each time enter is pressed.
//It controls the overall input and output
    function newEntry() {
        //if the message from the user isn't empty then run
        if (document.getElementById("chatbox").value != "") {
            //pulls the value from the chatbox ands sets it to lastUserMessage
            lastUserMessage = document.getElementById("chatbox").value;
            //sets the chat box to be clear
            document.getElementById("chatbox").value = "";
            //adds the value of the chatbox to the array messages
            messages.push(lastUserMessage);
            //Speech(lastUserMessage);  //says what the user typed outloud
            //sets the variable botMessage in response to lastUserMessage
            chatbotResponse();
            //add the chatbot's name and message to the array messages
            messages.push("<b>" + botName + ":</b> " + botMessage);
            // says the message using the text to speech function written below
            //Speech(botMessage);
            //outputs the last few array elements of messages to html
            // for (var i = 1; i < 8; i++) {
            //     if (messages[messages.length - i])
            //         document.getElementById("chatlog" + i).innerHTML = messages[messages.length - i];
            // }

//             // Get the chat container element
//             const chatContainer = document.getElementById('chatborder');
//
// // Loop through the messages array
//             for (let i = 0; i < messages.length; i++) {
//                 // Create a new <p> element
//                 const newMessage = document.createElement('p');
//
//                 // Add the class 'chatlog' to the new element
//                 newMessage.classList.add('chatlog');
//
//                 // Set the innerHTML of the new element to the corresponding message
//                 newMessage.innerHTML = messages[i];
//
//                 // Append the new element to the chat container
//                 chatContainer.appendChild(newMessage);
//             }

            const chatborder = document.getElementById('chatborder');
            var newMessage = document.createElement('p');
            newMessage.classList.add('chatlog');
            newMessage.textContent = lastUserMessage;
            chatborder.insertBefore(newMessage, chatborder.lastElementChild);

            newMessage = document.createElement('p');
            newMessage.classList.add('chatlog');
            //newMessage.textContent = "<b>" + botName + ":</b> " + botMessage;

            botMessage = "msg";//getResponse(session_id, lastUserMessage);
            getResponse(session_id, lastUserMessage)
                .then(function(data) {
                    botMessage = data; // Assign the data to the resultado variable

                    newMessage.innerHTML = "<b>" + botName + ":</b> " + botMessage;
                    console.log("msg: " + newMessage.textContent);
                    chatborder.insertBefore(newMessage, chatborder.lastElementChild);

                    const chatbox = document.getElementById('chatbox');
                    chatbox.scrollIntoView({ behavior: 'smooth' });
                })
                .catch(function(error) {
                    console.error(error); // Handle the error
                });


            // const chatborder = document.getElementById('chatborder');
            // chatborder.scrollTo(0, chatborder.scrollHeight);
        }
    }

//text to Speech
//https://developers.google.com/web/updates/2014/01/Web-apps-that-talk-Introduction-to-the-Speech-Synthesis-API
    function Speech(say) {
        if ('speechSynthesis' in window && talking) {
            var utterance = new SpeechSynthesisUtterance(say);
            //msg.voice = voices[10]; // Note: some voices don't support altering params
            //msg.voiceURI = 'native';
            //utterance.volume = 1; // 0 to 1
            //utterance.rate = 0.1; // 0.1 to 10
            //utterance.pitch = 1; //0 to 2
            //utterance.text = 'Hello World';
            //utterance.lang = 'en-US';
            speechSynthesis.speak(utterance);
        }
    }

//runs the keypress() function when a key is pressed
    document.onkeypress = keyPress;
//if the key pressed is 'enter' runs the function newEntry()
    function keyPress(e) {
        var x = e || window.event;
        var key = (x.keyCode || x.which);
        if (key == 13 || key == 3) {
            //runs this function when enter is pressed
            newEntry();
        }
        if (key == 38) {
            console.log('hi')
            //document.getElementById("chatbox").value = lastUserMessage;
        }
    }


    function scrollToBottom() {
        const container = document.getElementById('chatborder');
        container.scrollTop = container.scrollHeight;
    }

// Call the scrollToBottom function when the page loads
    window.addEventListener('load', scrollToBottom);

// Call the scrollToBottom function after adding new messages
    function addNewMessage() {
        // Add your code to append new messages to the chat container
        // ...

        scrollToBottom();
    }
});

//clears the placeholder text ion the chatbox
//this function is set to run when the users brings focus to the chatbox, by clicking on it
function placeHolder() {
    document.getElementById("chatbox").placeholder = "";
}

async function getResponse2(session_id, message) {
    try {
        const response = await fetch('/newMessage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'session_id=' + encodeURIComponent(session_id) + '&message=' + encodeURIComponent(message)
        });

        if (response.ok) {
            var data = await response.text();
            console.log('Resultado: ' + data);
            return data;
        } else {
            throw new Error('Request failed with status ' + response.status);
        }
    } catch (error) {
        return { error: error.message };
    }
}

function getResponse(session_id, message) {
    return new Promise(function(resolve, reject) {
        fetch('/newMessage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'session_id=' + encodeURIComponent(session_id) + '&message=' + encodeURIComponent(message)
        })
            .then(function(response) {
                if (response.ok) {
                    console.log('THERE ' + response.clone().text());
                    return response.clone().text();
                } else {
                    throw new Error('Request failed with status ' + response.status);
                }
            })
            .then(function(data) {
                resolve(data);
            })
            .catch(function(error) {
                reject(error);
            });
    });
}

