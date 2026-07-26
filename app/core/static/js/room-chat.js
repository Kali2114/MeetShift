document.addEventListener("DOMContentLoaded", () => {
    const threadContainer = document.querySelector(
        ".messages-thread[data-meeting-id]"
    );

    if (!threadContainer) {
        return;
    }

    const meetingId = threadContainer.dataset.meetingId;

    threadContainer.scrollTop = threadContainer.scrollHeight;

    const appendRoomMessage = (data) => {
        const messageId = String(data.id);

        if (threadContainer.querySelector(`[data-message-id="${messageId}"]`)) {
            return;
        }

        const item = document.createElement("div");
        item.classList.add("message-item", "message-item-received");
        item.dataset.messageId = messageId;

        const sender = document.createElement("p");
        sender.classList.add("message-sender");
        sender.textContent = data.sender_name;

        const content = document.createElement("p");
        content.classList.add("message-content");
        content.textContent = data.content;

        item.append(sender, content);
        threadContainer.appendChild(item);
        threadContainer.scrollTop = threadContainer.scrollHeight;
    };

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const roomSocket = new WebSocket(
        `${protocol}://${window.location.host}/ws/room/${meetingId}/`
    );

    roomSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.kind === "room_message") {
            appendRoomMessage(data);
        }
    };

    roomSocket.onerror = (error) => {
        console.error("Room WebSocket error:", error);
    };

    roomSocket.onclose = () => {
        console.warn("Room WebSocket connection closed.");
    };

    const messageForm = document.querySelector(".room-chat-form");
    const messageInput = messageForm?.querySelector("textarea");

    if (!messageForm || !messageInput) {
        return;
    }

    messageInput.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" || event.shiftKey) {
            return;
        }

        event.preventDefault();

        if (messageInput.value.trim() === "") {
            return;
        }

        messageForm.submit();
    });
});
