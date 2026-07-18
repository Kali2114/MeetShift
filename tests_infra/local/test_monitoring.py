"""Infrastructure tests for monitoring stack."""


def test_grafana_container_running(host):
    """Test Grafana container is running."""
    result = host.run(
        "docker inspect --format '{{.State.Running}}' meetshift-grafana-1"
    )

    assert result.stdout.strip() == "true"


def test_prometheus_container_running(host):
    """Test Prometheus container is running."""
    result = host.run(
        "docker inspect --format '{{.State.Running}}' meetshift-prometheus-1"
    )

    assert result.stdout.strip() == "true"


def test_grafana_http_endpoint(host):
    """Test Grafana HTTP endpoint is available."""
    result = host.run(
        "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/login')\""
    )

    assert result.rc == 0


def test_prometheus_http_endpoint(host):
    """Test Prometheus HTTP endpoint is available."""
    result = host.run(
        "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:9090/-/ready')\""
    )

    assert result.rc == 0
