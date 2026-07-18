"""Infrastructure tests for application network access."""


def test_app_port_is_listening(host):
    """Test application port is listening on host."""
    socket = host.socket("tcp://0.0.0.0:8000")

    assert socket.is_listening


def test_health_endpoint_available_from_host(host):
    """Test health endpoint is available from host."""
    result = host.run(
        'python -c "import urllib.request; '
        "urllib.request.urlopen('http://127.0.0.1:8000/health/', timeout=5)\""
    )

    assert result.rc == 0
