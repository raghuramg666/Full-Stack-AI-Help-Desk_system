let chatBox = document.getElementById("chat-box");
let usernameInput = document.getElementById("username");
let contactInput = document.getElementById("contact");
let categorySelect = document.getElementById("category");
let userMessageInput = document.getElementById("user-message");
let sendBtn = document.getElementById("send-btn");
let feedbackSection = document.getElementById("feedback-section");
let feedbackText = document.getElementById("feedback-text");
let submitFeedbackBtn = document.getElementById("submit-feedback-btn");
let newSessionBtn = document.getElementById("new-session-btn");
let statusLight = document.getElementById("status-light");
let statusText = document.getElementById("status-text");

let state = "username";
let username = "";
let contact = "";
let category = "";

function appendMessage(sender, text) {
    let msg = document.createElement("div");
    msg.className = sender;
    msg.innerText = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

sendBtn.addEventListener("click", async () => {
    if (state === "username") {
        username = usernameInput.value.trim();
        if (!username) return;
        appendMessage("user", username);
        usernameInput.style.display = "none";
        contactInput.style.display = "inline";
        state = "contact";
        appendMessage("bot", "Please enter your contact:");
    } else if (state === "contact") {
        contact = contactInput.value.trim();
        if (!contact) return;
        appendMessage("user", contact);
        contactInput.style.display = "none";
        categorySelect.style.display = "inline";
        state = "category";
        appendMessage("bot", "Select your issue category:");
    } else if (state === "category") {
        category = categorySelect.value;
        if (!category) return;
        appendMessage("user", category);
        categorySelect.style.display = "none";
        userMessageInput.style.display = "inline";
        state = "chat";
        appendMessage("bot", `Hi ${username}, how can I assist you today?`);
    } else if (state === "chat") {
        let message = userMessageInput.value.trim();
        if (!message) return;
        appendMessage("user", message);
        userMessageInput.value = "";

        const response = await fetch("/helpdesk", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, contact, request: message, category })
        });

        const result = await response.json();
        appendMessage("bot", result.response);

        // Update critical indicator
        if (result.escalate) {
            statusLight.style.backgroundColor = "red";
            statusText.textContent = "Status: CRITICAL – Escalation needed";
        } else {
            statusLight.style.backgroundColor = "green";
            statusText.textContent = "Status: OK – No escalation";
        }

        appendMessage("bot", "Is your query resolved? You can provide optional feedback or click 'End Session'.");
        feedbackSection.style.display = "block";
    }
});

submitFeedbackBtn.addEventListener("click", async () => {
    const feedback = feedbackText.value.trim();
    if (feedback) {
        await fetch("/feedback", {
            method: "POST",
            body: new URLSearchParams({ username, feedback })
        });
        appendMessage("bot", "🙏 Thanks for your feedback.");
    } else {
        appendMessage("bot", "Feedback skipped.");
    }
    feedbackSection.style.display = "none";
    userMessageInput.style.display = "none";
    newSessionBtn.style.display = "inline";
    statusLight.style.backgroundColor = "gray";
    statusText.textContent = "Status: Session ended";
});

newSessionBtn.addEventListener("click", () => {
    location.reload();
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendBtn.click();
    }
});
