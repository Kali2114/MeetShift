"""Production infrastructure tests for Nginx."""


def test_nginx_container_running(host):
    """Test Nginx container is running."""
    result = host.run("docker inspect --format '{{.State.Running}}' meetshift-nginx-1")

    assert result.stdout.strip() == "true"


def test_http_port_is_listening(host):
    """Test HTTP port 80 is listening."""
    socket = host.socket("tcp://0.0.0.0:80")

    assert socket.is_listening


def test_https_port_is_listening(host):
    """Test HTTPS port 443 is listening."""
    socket = host.socket("tcp://0.0.0.0:443")

    assert socket.is_listening


def test_health_endpoint_through_nginx(host):
    """Test Nginx serves the application health endpoint."""
    result = host.run(
        'python3 -c "import urllib.request; '
        "urllib.request.urlopen('https://meetshift.org/health/', timeout=10)\""
    )

    assert result.rc == 0
