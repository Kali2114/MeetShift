"""Infrastructure tests for MeetShift deployment."""


def test_docker_service_running(host):
    """Test Docker service is running."""
    service = host.service("docker")

    assert service.is_running
    assert service.is_enabled


def test_app_container_running(host):
    """Test application container is running."""
    result = host.run("docker inspect --format '{{.State.Running}}' meetshift-app-1")

    assert result.stdout.strip() == "true"


def test_app_container_healthy(host):
    """Test application container is healthy."""
    result = host.run(
        "docker inspect --format '{{.State.Health.Status}}' meetshift-app-1"
    )

    assert result.stdout.strip() == "healthy"


def test_health_endpoint(host):
    """Test application health endpoint returns HTTP 200."""
    result = host.run(
        'python -c "import urllib.request; '
        "urllib.request.urlopen('http://127.0.0.1:8000/health/')\""
    )

    assert result.rc == 0
