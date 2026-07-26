const SENDER_COLOR_PALETTE = [
    "#2563eb",
    "#e11d48",
    "#7c3aed",
    "#0891b2",
    "#059669",
    "#db2777",
];

const senderColor = (senderId) =>
    SENDER_COLOR_PALETTE[senderId % SENDER_COLOR_PALETTE.length];

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
        item.style.setProperty("--sender-color", senderColor(data.sender_id));

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

    const onlineList = document.querySelector("#room-online-list");

    const updateOnlineUsers = (onlineUsers) => {
        if (!onlineList) {
            return;
        }

        onlineList.textContent = onlineUsers.length
            ? onlineUsers.map((onlineUser) => onlineUser.name).join(", ")
            : "Nobody yet";
    };

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";

    connectWithReconnect(
        () => `${protocol}://${window.location.host}/ws/room/${meetingId}/`,
        {
            onMessage: (data) => {
                if (data.kind === "room_message") {
                    appendRoomMessage(data);
                } else if (data.kind === "room_presence") {
                    updateOnlineUsers(data.online_users);
                }
            },
        }
    );

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
