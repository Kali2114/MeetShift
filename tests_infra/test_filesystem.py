"""Infrastructure tests for Docker volumes."""


def test_media_volume_exists(host):
    """Test media Docker volume exists."""
    result = host.run("docker volume inspect meetshift_media-data")

    assert result.rc == 0


def test_static_volume_exists(host):
    """Test static Docker volume exists."""
    result = host.run("docker volume inspect meetshift_static-data")

    assert result.rc == 0


def test_logs_volume_exists(host):
    """Test application logs Docker volume exists."""
    result = host.run("docker volume inspect meetshift_app-logs")

    assert result.rc == 0


def test_coverage_volume_exists(host):
    """Test coverage Docker volume exists."""
    result = host.run("docker volume inspect meetshift_coverage-data")

    assert result.rc == 0
