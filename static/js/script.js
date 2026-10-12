
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const chatBox = document.getElementById("chat-box");
const sendBtn = document.getElementById("send-btn");


function addMessage(text, isUser = false) {

    const wrapper = document.createElement("div");

    wrapper.className = `flex ${
        isUser ? "justify-end" : "justify-start"
    }`;

    const bubble = document.createElement("div");

    bubble.className = `rounded-lg p-3 max-w-[80%] shadow ${
        isUser
            ? "bg-blue-600 text-white"
            : "bg-white text-gray-800 whitespace-pre-wrap"
    }`;

    bubble.textContent = text;

    wrapper.appendChild(bubble);
    chatBox.appendChild(wrapper);

    chatBox.scrollTop = chatBox.scrollHeight;
}


chatForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    const userText = messageInput.value.trim();

    if (!userText) {
        return;
    }


    addMessage(userText, true);

    messageInput.value = "";


    sendBtn.disabled = true;
    sendBtn.textContent = "...";


    try {

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: userText
            })

        });


        if (!response.ok) {
            throw new Error("Server returned an error");
        }


        const data = await response.json();


        addMessage(data.response, false);

    }

    catch (error) {

        console.error("Chat error:", error);

        addMessage(
            "Error: Could not connect to the server.",
            false
        );

    }

    finally {

        sendBtn.disabled = false;
        sendBtn.textContent = "Send";

        messageInput.focus();
    }

});
