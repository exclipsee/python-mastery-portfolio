from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app
from python_mastery_portfolio.system_metrics import get_system_metrics
from python_mastery_portfolio.websocket_manager import ConnectionManager


def test_system_metrics_collection() -> None:
    """Test system metrics collection (mocked to avoid psutil dependency)."""
    with patch("python_mastery_portfolio.system_metrics.psutil") as mock_psutil:
        # Mock psutil objects
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.virtual_memory.return_value = Mock(
            percent=60.0,
            used=8 * 1024 * 1024 * 1024,  # 8GB
            total=16 * 1024 * 1024 * 1024,  # 16GB
        )
        mock_psutil.disk_usage.return_value = Mock(
            used=500 * 1024 * 1024 * 1024,  # 500GB
            total=1000 * 1024 * 1024 * 1024,  # 1TB
        )
        mock_psutil.net_connections.return_value = [
            Mock(status="ESTABLISHED"),
            Mock(status="ESTABLISHED"),
            Mock(status="LISTEN"),
        ]
        mock_psutil.CONN_ESTABLISHED = "ESTABLISHED"
        mock_psutil.boot_time.return_value = 1635724800.0
        
        metrics = get_system_metrics()
        
        assert metrics is not None
        assert metrics.cpu_percent == 25.5
        assert metrics.memory_percent == 60.0
        assert metrics.memory_used_mb == 8192.0
        assert metrics.memory_total_mb == 16384.0
        assert abs(metrics.disk_usage_percent - 50.0) < 0.1  # 500/1000 * 100
        assert metrics.active_connections == 2  # Only ESTABLISHED connections
        assert metrics.boot_time == 1635724800.0


def test_connection_manager() -> None:
    """Test WebSocket connection manager."""
    manager = ConnectionManager()
    
    # Mock WebSocket
    mock_ws1 = Mock()
    mock_ws2 = Mock()
    
    # Test initial state
    assert manager.get_connection_count() == 0
    
    # Test adding connections
    manager.active_connections.append(mock_ws1)
    manager.active_connections.append(mock_ws2)
    assert manager.get_connection_count() == 2
    
    # Test disconnect
    manager.disconnect(mock_ws1)
    assert manager.get_connection_count() == 1
    assert mock_ws2 in manager.active_connections
    assert mock_ws1 not in manager.active_connections


def test_websocket_connections_endpoint() -> None:
    """Test the WebSocket connections monitoring endpoint."""
    client = TestClient(app)
    r = client.get("/monitor/connections")
    assert r.status_code == 200
    data = r.json()
    assert "active_connections" in data
    assert isinstance(data["active_connections"], int)


def test_websocket_endpoint() -> None:
    """Test WebSocket endpoint connection."""
    client = TestClient(app)
    
    # Test WebSocket connection
    with client.websocket_connect("/ws/metrics") as websocket:
        # Connection should be established
        # We don't need to test actual message sending as that's handled by background task
        
        # Send a test message (though metrics endpoint doesn't expect any)
        websocket.send_text("test")
        
        # The connection should stay open
        # In a real test, we might wait for metrics messages, but for unit test
        # we'll just verify the connection works
        pass