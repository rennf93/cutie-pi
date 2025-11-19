"""System information gathering utilities"""

import subprocess
import time


class SystemInfo:
    """Gathers system information from the Raspberry Pi"""

    def __init__(self) -> None:
        self.cpu_percent = 0.0
        self.mem_percent = 0.0
        self.mem_used = 0.0
        self.mem_total = 0.0
        self.disk_used = 0.0
        self.disk_total = 0.0
        self.disk_percent = 0.0
        self.temp = 0.0
        self.uptime = ""
        self.ip_address = ""
        self.hostname = ""
        self.fan_speed = 0
        self.fan_rpm = 0
        self.last_update = 0.0
        self._last_cpu: tuple[int, int] | None = None

    def update(self, interval: float = 2.0) -> None:
        """Update system info if enough time has passed"""
        current_time = time.time()
        if current_time - self.last_update > interval:
            self._fetch_all()
            self.last_update = current_time

    def _fetch_all(self) -> None:
        """Fetch all system information"""
        try:
            self._fetch_cpu()
            self._fetch_memory()
            self._fetch_disk()
            self._fetch_temperature()
            self._fetch_uptime()
            self._fetch_network()
            self._fetch_fan()
        except Exception as e:
            print(f"Error getting system info: {e}")

    def _fetch_cpu(self) -> None:
        """Fetch CPU usage from /proc/stat"""
        try:
            with open("/proc/stat", "r") as f:
                cpu_line = f.readline()
                cpu_times = list(map(int, cpu_line.split()[1:]))
                idle = cpu_times[3]
                total = sum(cpu_times)
                if self._last_cpu is not None:
                    idle_delta = idle - self._last_cpu[0]
                    total_delta = total - self._last_cpu[1]
                    if total_delta > 0:
                        self.cpu_percent = 100 * (1 - idle_delta / total_delta)
                self._last_cpu = (idle, total)
        except Exception as e:
            print(f"Error getting CPU: {e}")

    def _fetch_memory(self) -> None:
        """Fetch memory usage from /proc/meminfo"""
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo: dict[str, int] = {}
                for line in f:
                    parts = line.split()
                    meminfo[parts[0].rstrip(":")] = int(parts[1])
                self.mem_total = meminfo.get("MemTotal", 0) / 1024  # MB
                mem_available = meminfo.get("MemAvailable", 0) / 1024
                self.mem_used = self.mem_total - mem_available
                self.mem_percent = (
                    (self.mem_used / self.mem_total * 100) if self.mem_total > 0 else 0
                )
        except Exception as e:
            print(f"Error getting memory: {e}")

    def _fetch_disk(self) -> None:
        """Fetch disk usage"""
        try:
            result = subprocess.run(
                ["df", "-B1", "/"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    parts = lines[1].split()
                    self.disk_total = int(parts[1]) / (1024**3)  # GB
                    self.disk_used = int(parts[2]) / (1024**3)
                    self.disk_percent = (
                        (self.disk_used / self.disk_total * 100) if self.disk_total > 0 else 0
                    )
        except Exception as e:
            print(f"Error getting disk: {e}")

    def _fetch_temperature(self) -> None:
        """Fetch CPU temperature"""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                self.temp = int(f.read().strip()) / 1000
        except Exception as e:
            print(f"Error getting temperature: {e}")
            self.temp = 0

    def _fetch_uptime(self) -> None:
        """Fetch system uptime"""
        try:
            with open("/proc/uptime", "r") as f:
                uptime_secs = float(f.read().split()[0])
                days = int(uptime_secs // 86400)
                hours = int((uptime_secs % 86400) // 3600)
                mins = int((uptime_secs % 3600) // 60)
                if days > 0:
                    self.uptime = f"{days}d {hours}h {mins}m"
                else:
                    self.uptime = f"{hours}h {mins}m"
        except Exception as e:
            print(f"Error getting uptime: {e}")
            self.uptime = "N/A"

    def _fetch_network(self) -> None:
        """Fetch IP address and hostname"""
        try:
            result = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            self.ip_address = (
                result.stdout.strip().split()[0] if result.stdout.strip() else "N/A"
            )
        except Exception as e:
            print(f"Error getting IP address: {e}")
            self.ip_address = "N/A"

        try:
            with open("/etc/hostname", "r") as f:
                self.hostname = f.read().strip()
        except Exception as e:
            print(f"Error getting hostname: {e}")
            self.hostname = "unknown"

    def _fetch_fan(self) -> None:
        """Fetch fan speed (RPM) for Pi 5"""
        fan_rpm_paths = [
            "/sys/devices/platform/cooling_fan/hwmon/hwmon2/fan1_input",
            "/sys/devices/platform/cooling_fan/hwmon/hwmon3/fan1_input",
            "/sys/devices/platform/cooling_fan/hwmon/hwmon1/fan1_input",
        ]

        for fan_path in fan_rpm_paths:
            try:
                with open(fan_path, "r") as f:
                    self.fan_rpm = int(f.read().strip())
                    # Convert RPM to percentage (max ~10000 RPM for Pi 5 fan)
                    self.fan_speed = min(255, int((self.fan_rpm / 10000) * 255))
                    return
            except Exception:
                continue

        self.fan_rpm = 0
        self.fan_speed = 0
