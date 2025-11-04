"""System metrics collection utilities for real-time monitoring."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import asdict, dataclass
from typing import Any

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class SystemMetrics:
    """System metrics snapshot."""
    
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    active_connections: int
    boot_time: float


def get_system_metrics() -> SystemMetrics | None:
    """Collect current system metrics.
    
    Returns None if psutil is not available.
    """
    if psutil is None:
        return None
    
    try:
        # CPU usage (non-blocking)
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # Disk usage (root/primary partition)
        if hasattr(psutil, "disk_usage"):
            disk = psutil.disk_usage("/")
        else:
            disk = psutil.disk_usage("C:\\")
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_total_gb = disk.total / (1024 * 1024 * 1024)
        
        # Network connections
        connections = psutil.net_connections(kind="inet")
        active_connections = len([c for c in connections if c.status == psutil.CONN_ESTABLISHED])
        
        # Boot time
        boot_time = psutil.boot_time()
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_total_mb=memory_total_mb,
            disk_usage_percent=disk_usage_percent,
            disk_used_gb=disk_used_gb,
            disk_total_gb=disk_total_gb,
            active_connections=active_connections,
            boot_time=boot_time,
        )
    except Exception:
        # Return None on any error
        return None


async def metrics_broadcaster(websocket_manager: Any, interval: float = 2.0) -> None:
    """Continuously broadcast system metrics via WebSocket.
    
    Args:
        websocket_manager: WebSocket connection manager
        interval: Seconds between metric broadcasts
    """
    while True:
        metrics = get_system_metrics()
        if metrics is not None:
            payload = {
                "type": "system_metrics",
                "data": asdict(metrics)
            }
            await websocket_manager.broadcast(json.dumps(payload))
        
        await asyncio.sleep(interval)