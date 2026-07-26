function connectWithReconnect(buildUrl, handlers) {
    const initialDelay = 1000;
    const maxDelay = 30000;
    let delay = initialDelay;

    const connect = () => {
        const socket = new WebSocket(buildUrl());

        socket.onopen = () => {
            delay = initialDelay;
            handlers.onOpen?.();
        };

        socket.onmessage = (event) => {
            handlers.onMessage(JSON.parse(event.data));
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        socket.onclose = () => {
            console.warn(`WebSocket closed, reconnecting in ${delay}ms`);
            window.setTimeout(connect, delay);
            delay = Math.min(delay * 2, maxDelay);
        };
    };

    connect();
}
