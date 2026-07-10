"""Infrastructure tests for Redis container."""


def test_redis_container_running(host):
    """Test Redis container is running."""
    result = host.run("docker inspect --format '{{.State.Running}}' meetshift-redis-1")

    assert result.stdout.strip() == "true"


def test_redis_accepts_connections(host):
    """Test Redis accepts connections."""
    result = host.run("docker exec meetshift-redis-1 redis-cli ping")

    assert result.stdout.strip() == "PONG"
