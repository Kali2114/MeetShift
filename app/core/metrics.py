"""
Prometheus metrics for real-time WebSocket connections.
"""

from prometheus_client import Counter, Gauge

websocket_connections_active = Gauge(
    "websocket_connections_active",
    "Currently open WebSocket connections.",
    ["consumer"],
)

websocket_connections_total = Counter(
    "websocket_connections_total",
    "Total WebSocket connections accepted.",
    ["consumer"],
)

websocket_disconnections_total = Counter(
    "websocket_disconnections_total",
    "Total WebSocket disconnections.",
    ["consumer"],
)
