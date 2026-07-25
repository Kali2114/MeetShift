document.addEventListener("DOMContentLoaded", () => {
    const badge = document.querySelector("#notification-badge");
    const messagesBadge = document.querySelector("#messages-badge");
    const toastContainer = document.querySelector(
        "#notification-toast-container"
    );

    if (!badge || !toastContainer) {
        return;
    }

    const receivedNotificationIds = new Set();

    const initialUnreadCount = Number(badge.textContent.trim());

    badge.style.display = initialUnreadCount > 0
        ? "inline-block"
        : "none";

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";

    const notificationSocket = new WebSocket(
        `${protocol}://${window.location.host}/ws/notifications/`
    );

    const removeToast = (toast) => {
        toast.classList.add("notification-toast-removing");

        window.setTimeout(() => {
            toast.remove();
        }, 250);
    };

    const showNotificationToast = (data) => {
        const toast = document.createElement("div");
        toast.classList.add("notification-toast");

        const title = document.createElement("p");
        title.classList.add("notification-toast-title");
        title.textContent = data.conversation_id ? "New message" : "New notification";

        const message = document.createElement("p");
        message.classList.add("notification-toast-message");
        message.textContent = data.message;

        toast.append(title, message);
        toastContainer.appendChild(toast);

        toast.addEventListener("click", () => {
            window.location.href = `/user/notifications/${data.id}/read/`;
        });

        window.setTimeout(() => {
            removeToast(toast);
        }, 5000);
    };

    const appendMessageToThread = (threadContainer, data) => {
        const item = document.createElement("div");
        item.classList.add("message-item", "message-item-received");
        item.dataset.messageId = data.id;

        const content = document.createElement("p");
        content.classList.add("message-content");
        content.textContent = data.message;

        item.append(content);
        threadContainer.appendChild(item);
        threadContainer.scrollTop = threadContainer.scrollHeight;
    };

    const handleConversationUpdate = (data) => {
        if (messagesBadge) {
            messagesBadge.textContent = data.total_unread_count;
            messagesBadge.style.display = data.total_unread_count > 0
                ? "inline-block"
                : "none";
        }

        const threadContainer = document.querySelector(
            `.messages-thread[data-conversation-id="${data.conversation_id}"]`
        );

        if (threadContainer) {
            appendMessageToThread(threadContainer, data);
            return;
        }

        const conversationsList = document.querySelector(
            ".messenger-conversation-list"
        );

        if (!conversationsList) {
            return;
        }

        const row = conversationsList.querySelector(
            `[data-conversation-id="${data.conversation_id}"]`
        );

        if (!row) {
            window.location.reload();
            return;
        }

        let unreadBadge = row.querySelector(".conversation-unread-count");

        if (data.unread_count > 0) {
            row.classList.add("unread");

            if (!unreadBadge) {
                unreadBadge = document.createElement("span");
                unreadBadge.classList.add("conversation-unread-count");
                row.appendChild(unreadBadge);
            }

            unreadBadge.textContent = data.unread_count;
        }

        conversationsList.prepend(row);
    };

    notificationSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.kind === "conversation_update") {
            console.log("Received conversation update:", data);
            handleConversationUpdate(data);
            return;
        }

        const notificationId = String(data.id);
        const unreadCount = Number(data.unread_count);

        console.log("Received notification:", data);

        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0
            ? "inline-block"
            : "none";

        if (receivedNotificationIds.has(notificationId)) {
            console.log(
                "Duplicate notification ignored:",
                notificationId
            );
            return;
        }

        receivedNotificationIds.add(notificationId);
        showNotificationToast(data);
    };

    notificationSocket.onerror = (error) => {
        console.error("Notification WebSocket error:", error);
    };

    notificationSocket.onclose = () => {
        console.warn("Notification WebSocket connection closed.");
    };
});

document.addEventListener("DOMContentLoaded", () => {
    const threadContainer = document.querySelector(".messages-thread");

    if (threadContainer) {
        threadContainer.scrollTop = threadContainer.scrollHeight;
    }

    const messageForm = document.querySelector(".message-form");
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

window.addEventListener("pageshow", (event) => {
    const navigationEntry = performance
        .getEntriesByType("navigation")[0];

    const isBackForwardNavigation =
        navigationEntry?.type === "back_forward";

    if (event.persisted || isBackForwardNavigation) {
        window.location.reload();
    }
});
