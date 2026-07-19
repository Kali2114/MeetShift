document.addEventListener("DOMContentLoaded", () => {
    const badge = document.querySelector("#notification-badge");
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
        title.textContent = "New notification";

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

    notificationSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
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

window.addEventListener("pageshow", (event) => {
    const navigationEntry = performance
        .getEntriesByType("navigation")[0];

    const isBackForwardNavigation =
        navigationEntry?.type === "back_forward";

    if (event.persisted || isBackForwardNavigation) {
        window.location.reload();
    }
});
