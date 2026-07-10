"""Infrastructure tests for PostgreSQL container."""


def test_postgres_container_running(host):
    """Test PostgreSQL container is running."""
    result = host.run("docker inspect --format '{{.State.Running}}' meetshift-db-1")

    assert result.stdout.strip() == "true"


def test_postgres_volume_exists(host):
    """Test PostgreSQL Docker volume exists."""
    result = host.run("docker volume inspect meetshift_dev-db-data")

    assert result.rc == 0
