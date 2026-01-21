#!/usr/bin/env python3
"""I2C Manager (single owner of /dev/i2c-*)

- Reads:
  - INA219 (bus voltage / current / power)
  - VL53L1X (distance)
  - MPU6050 (accel / gyro / temp) [optional]
- Displays on OLED:
  - Wi-Fi mode (STA/AP), SSID, IP
  - Battery percent (INA219 voltage-based)
- IPC:
  - Unix Domain Socket (datagram) server: /run/afb_i2c.sock
  - Request: JSON bytes (e.g. {"cmd":"get"})
  - Response: JSON dict with latest cached readings

This process should be started by systemd using the venv python:
  ExecStart=/home/pi/.afbvenv/bin/python3 .../i2c_manager.py

Notes:
- Keep this as the ONLY process that touches I2C devices.
- Other processes must read sensor values via IPC (UDS) from this manager.
"""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import board
import busio
from PIL import Image, ImageDraw, ImageFont

import adafruit_ssd1306
from adafruit_ina219 import INA219
import adafruit_vl53l1x

try:
    import adafruit_mpu6050
except Exception:  # pragma: no cover
    adafruit_mpu6050 = None  # type: ignore


# ----------------------------
# Configuration
# ----------------------------

UDS_PATH = "/run/afb_i2c.sock"

OLED_WIDTH = 128
OLED_HEIGHT = 32

# Update rates (Hz)
SENSOR_HZ_VL53 = 30.0
SENSOR_HZ_INA = 10.0
SENSOR_HZ_MPU = 100.0
OLED_HZ = 2.0

# Battery percent estimation from INA219 bus voltage (2S Li-ion default)
# - Use a LUT (piecewise linear interpolation) for a more realistic SoC curve.
# - Apply EMA smoothing to reduce jitter from load-induced voltage ripple.
#
# You MUST tune this LUT for your battery, wiring, and load.
# Values are pack voltage (V) -> percent (%).
BAT_LUT_2S = [
    (6.40, 0),
    (6.60, 5),
    (6.80, 10),
    (7.00, 20),
    (7.20, 35),
    (7.40, 50),
    (7.60, 65),
    (7.80, 80),
    (8.00, 92),
    (8.20, 100),
]

# EMA filter alpha: 0..1 (higher = less smoothing, more responsive)
BAT_VOLT_EWA_ALPHA = 0.25


# ----------------------------
# Helpers
# ----------------------------


def _run_cmd(cmd: list[str], timeout_s: float = 1.0) -> Tuple[int, str]:
    """Run a command and return (returncode, stdout_str)."""
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=timeout_s)
        return 0, out.decode("utf-8", errors="replace").strip()
    except subprocess.CalledProcessError as e:
        return int(e.returncode), ""
    except Exception:
        return 1, ""


def get_ssid() -> str:
    """Best-effort SSID read for STA mode."""
    # iwgetid is commonly available on Raspberry Pi OS
    rc, out = _run_cmd(["iwgetid", "-r"], timeout_s=0.8)
    if rc == 0 and out:
        return out

    # Fallback to nmcli if installed
    rc, out = _run_cmd(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"], timeout_s=1.0)
    if rc == 0 and out:
        # Lines look like: yes:<ssid>
        for line in out.splitlines():
            if line.startswith("yes:"):
                return line.split(":", 1)[1].strip()

    return ""


def get_ip_addr(ifname: str) -> str:
    """Get IPv4 address for an interface via `ip` (no extra deps)."""
    rc, out = _run_cmd(["ip", "-4", "addr", "show", ifname], timeout_s=0.8)
    if rc != 0 or not out:
        return ""

    # Parse 'inet X.X.X.X/..'
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("inet "):
            ip_with_mask = line.split()[1]
            return ip_with_mask.split("/")[0]
    return ""


def detect_mode_and_ip() -> Tuple[str, str, str]:
    """Return (mode, ssid, ip).

    Heuristic:
    - If an SSID exists: STA
    - Else if hostapd is active: AP
    - Else: UNKNOWN

    IP is chosen in order: wlan0, eth0.
    """
    ssid = get_ssid()

    if ssid:
        mode = "STA"
    else:
        rc, out = _run_cmd(["systemctl", "is-active", "hostapd"], timeout_s=0.6)
        mode = "AP" if (rc == 0 and out.strip() == "active") else "UNKNOWN"

    ip = get_ip_addr("wlan0")
    if not ip:
        ip = get_ip_addr("eth0")

    return mode, ssid, ip


def estimate_battery_percent(bus_voltage_v: Optional[float]) -> Optional[int]:
    """Estimate battery percent from pack voltage using LUT interpolation.

    - Voltages above the highest LUT voltage are clamped to 100%.
    - Voltages below the lowest LUT voltage are clamped to 0%.

    The LUT is defined by BAT_LUT_2S and assumed to be sorted by voltage.
    """
    if bus_voltage_v is None:
        return None

    v = float(bus_voltage_v)
    lut = BAT_LUT_2S

    if not lut:
        return None

    # Clamp to ends
    if v <= lut[0][0]:
        return int(lut[0][1])
    if v >= lut[-1][0]:
        return int(lut[-1][1])

    # Find segment and interpolate
    for (v0, p0), (v1, p1) in zip(lut[:-1], lut[1:]):
        if v0 <= v <= v1:
            if v1 == v0:
                return int(p1)
            t = (v - v0) / (v1 - v0)
            pct = p0 + t * (p1 - p0)
            return int(round(max(0.0, min(100.0, pct))))

    # Fallback (should not happen)
    return int(lut[-1][1])


# ----------------------------
# Shared state
# ----------------------------


@dataclass
class SensorCache:
    ts: float = 0.0
    distance_mm: Optional[int] = None
    imu_accel_m_s2: Optional[Tuple[float, float, float]] = None
    imu_gyro_rad_s: Optional[Tuple[float, float, float]] = None
    imu_temp_c: Optional[float] = None
    bus_voltage_v: Optional[float] = None
    bus_voltage_v_raw: Optional[float] = None
    bus_voltage_v_filt: Optional[float] = None
    current_mA: Optional[float] = None
    power_mW: Optional[float] = None
    battery_percent: Optional[int] = None
    mode: str = ""
    ssid: str = ""
    ip: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts,
            "distance_mm": self.distance_mm,
            "ina219": {
                "bus_voltage_v": self.bus_voltage_v,
                "bus_voltage_v_raw": self.bus_voltage_v_raw,
                "bus_voltage_v_filt": self.bus_voltage_v_filt,
                "current_mA": self.current_mA,
                "power_mW": self.power_mW,
            },
            "battery_percent": self.battery_percent,
            "net": {
                "mode": self.mode,
                "ssid": self.ssid,
                "ip": self.ip,
            },
        }

    def to_ipc_dict(self) -> Dict[str, Any]:
        """Return a minimal payload for IPC consumers (driving/control loops)."""
        return {
            "ts": self.ts,
            "distance_mm": self.distance_mm,
            "imu": {
                "accel_m_s2": self.imu_accel_m_s2,
                "gyro_rad_s": self.imu_gyro_rad_s,
                "temp_c": self.imu_temp_c,
            },
        }


# ----------------------------
# Main I2C manager
# ----------------------------


class I2CManager:
    def __init__(self) -> None:
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.cache = SensorCache()

        # I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Devices
        self.ina = INA219(self.i2c)
        # Optional distance sensor (VL53L1X)
        self.tof = None
        try:
            self.tof = adafruit_vl53l1x.VL53L1X(self.i2c)
            self.tof.distance_mode = 1  # short
            self.tof.timing_budget = 100  # ms
            self.tof.start_ranging()
        except Exception:
            self.tof = None

        # Optional IMU (MPU6050)
        self.mpu = None
        if adafruit_mpu6050 is not None:
            try:
                self.mpu = adafruit_mpu6050.MPU6050(self.i2c)
            except Exception:
                self.mpu = None

        self.oled = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, self.i2c)
        self.oled.fill(0)
        self.oled.show()

        # OLED drawing objects
        self.font = ImageFont.load_default()

        # UDS server socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        # Ensure /run exists and clean old socket
        os.makedirs(os.path.dirname(UDS_PATH), exist_ok=True)
        try:
            if os.path.exists(UDS_PATH):
                os.unlink(UDS_PATH)
        except Exception:
            pass

        self.sock.bind(UDS_PATH)
        # Make it readable by non-root users (education-friendly)
        try:
            os.chmod(UDS_PATH, 0o666)
        except Exception:
            pass

        # EMA state for battery voltage smoothing
        self._bus_v_ema: Optional[float] = None

    def close(self) -> None:
        # Clear OLED on shutdown
        try:
            self.oled.fill(0)
            self.oled.show()
        except Exception:
            pass

        if self.tof is not None:
            try:
                self.tof.stop_ranging()
            except Exception:
                pass

        try:
            self.sock.close()
        except Exception:
            pass

        try:
            if os.path.exists(UDS_PATH):
                os.unlink(UDS_PATH)
        except Exception:
            pass

    # ------------------------
    # Worker loops
    # ------------------------

    def _loop_vl53(self) -> None:
        period = 1.0 / max(SENSOR_HZ_VL53, 1.0)
        while not self.stop_event.is_set():
            t0 = time.time()

            dist = None

            if self.tof is not None:
                try:
                    d = self.tof.distance
                    if d is not None:
                        dist = int(d)
                except Exception:
                    dist = None

            with self.lock:
                self.cache.distance_mm = dist
                self.cache.ts = time.time()

            dt = time.time() - t0
            time.sleep(max(0.0, period - dt))

    def _loop_mpu6050(self) -> None:
        """Read MPU6050 at a higher rate and cache the latest values."""
        period = 1.0 / max(SENSOR_HZ_MPU, 1.0)
        while not self.stop_event.is_set():
            t0 = time.time()

            accel = gyro = None
            temp_c = None

            if self.mpu is not None:
                try:
                    ax, ay, az = self.mpu.acceleration  # m/s^2
                    gx, gy, gz = self.mpu.gyro  # rad/s
                    accel = (float(ax), float(ay), float(az))
                    gyro = (float(gx), float(gy), float(gz))
                    temp_c = float(self.mpu.temperature)
                except Exception:
                    accel = gyro = None
                    temp_c = None

            with self.lock:
                self.cache.imu_accel_m_s2 = accel
                self.cache.imu_gyro_rad_s = gyro
                self.cache.imu_temp_c = temp_c
                # Do not overwrite ts too aggressively if IMU is absent
                if self.mpu is not None:
                    self.cache.ts = time.time()

            dt = time.time() - t0
            time.sleep(max(0.0, period - dt))

    def _loop_ina219(self) -> None:
        period = 1.0 / max(SENSOR_HZ_INA, 1.0)
        while not self.stop_event.is_set():
            t0 = time.time()

            bus_v_raw = cur_mA = p_mW = None
            bus_v_ema = None
            batt_pct = None

            try:
                bus_v_raw = float(self.ina.bus_voltage)
                cur_mA = float(self.ina.current)
                p_mW = float(self.ina.power)

                if self._bus_v_ema is None:
                    self._bus_v_ema = bus_v_raw
                else:
                    a = float(BAT_VOLT_EWA_ALPHA)
                    a = max(0.0, min(1.0, a))
                    self._bus_v_ema = a * bus_v_raw + (1.0 - a) * self._bus_v_ema

                bus_v_ema = self._bus_v_ema
                batt_pct = estimate_battery_percent(bus_v_ema)
            except Exception:
                bus_v_raw = cur_mA = p_mW = None
                bus_v_ema = None
                batt_pct = None

            with self.lock:
                # Keep bus_voltage_v as the filtered voltage for backward compatibility
                self.cache.bus_voltage_v = bus_v_ema
                self.cache.bus_voltage_v_raw = bus_v_raw
                self.cache.bus_voltage_v_filt = bus_v_ema
                self.cache.current_mA = cur_mA
                self.cache.power_mW = p_mW
                self.cache.battery_percent = batt_pct
                self.cache.ts = time.time()

            dt = time.time() - t0
            time.sleep(max(0.0, period - dt))

    def _loop_status(self) -> None:
        # Network + battery are slow-changing; update at OLED rate
        period = 1.0 / max(OLED_HZ, 1.0)
        while not self.stop_event.is_set():
            t0 = time.time()

            mode, ssid, ip = detect_mode_and_ip()

            with self.lock:
                self.cache.mode = mode
                self.cache.ssid = ssid
                self.cache.ip = ip
                self.cache.ts = time.time()

            dt = time.time() - t0
            time.sleep(max(0.0, period - dt))

    def _loop_oled(self) -> None:
        period = 1.0 / max(OLED_HZ, 1.0)
        while not self.stop_event.is_set():
            t0 = time.time()

            with self.lock:
                mode = self.cache.mode
                ssid = self.cache.ssid
                ip = self.cache.ip
                batt = self.cache.battery_percent
                dist = self.cache.distance_mm

            # Build 3 lines for 128x32 (default font ~8px)
            # Line1: MODE + battery
            batt_str = "--" if batt is None else f"{batt:3d}%"
            line1 = f"{mode:<7} BAT:{batt_str}"

            # Line2: SSID (trim)
            ssid_show = ssid if ssid else "(no ssid)"
            if len(ssid_show) > 16:
                ssid_show = ssid_show[:16]
            line2 = f"SSID:{ssid_show}"

            # Line3: IP + distance
            ip_show = ip if ip else "0.0.0.0"
            dist_str = "----" if dist is None else f"{dist:4d}"
            line3 = f"IP:{ip_show} D:{dist_str}"
            if len(line3) > 21:
                line3 = line3[:21]

            try:
                img = Image.new("1", (OLED_WIDTH, OLED_HEIGHT))
                draw = ImageDraw.Draw(img)
                draw.text((0, 0), line1, font=self.font, fill=255)
                draw.text((0, 11), line2, font=self.font, fill=255)
                draw.text((0, 22), line3, font=self.font, fill=255)
                self.oled.image(img)
                self.oled.show()
            except Exception:
                # Do not crash on OLED write errors
                pass

            dt = time.time() - t0
            time.sleep(max(0.0, period - dt))

    def _loop_uds_server(self) -> None:
        # Non-blocking with timeout so we can exit quickly
        self.sock.settimeout(0.5)

        while not self.stop_event.is_set():
            try:
                data, addr = self.sock.recvfrom(4096)
            except socket.timeout:
                continue
            except Exception:
                continue

            # Default response
            with self.lock:
                payload = self.cache.to_ipc_dict()

            # Parse request (optional)
            try:
                req = json.loads(data.decode("utf-8", errors="replace")) if data else {}
                cmd = req.get("cmd", "get")
                if cmd != "get":
                    payload["error"] = f"unknown cmd: {cmd}"
            except Exception:
                payload["error"] = "bad request"

            try:
                resp = json.dumps(payload, separators=(",", ":")).encode("utf-8")
                self.sock.sendto(resp, addr)
            except Exception:
                pass

    def run(self) -> None:
        threads = [
            threading.Thread(target=self._loop_vl53, name="vl53", daemon=True),
            threading.Thread(target=self._loop_mpu6050, name="mpu6050", daemon=True),
            threading.Thread(target=self._loop_ina219, name="ina219", daemon=True),
            threading.Thread(target=self._loop_status, name="status", daemon=True),
            threading.Thread(target=self._loop_oled, name="oled", daemon=True),
            threading.Thread(target=self._loop_uds_server, name="uds", daemon=True),
        ]

        for th in threads:
            th.start()

        # Main wait loop
        while not self.stop_event.is_set():
            time.sleep(0.2)


# ----------------------------
# Entrypoint
# ----------------------------


def main() -> None:
    mgr = I2CManager()

    def _handle_signal(_signum: int, _frame: Any) -> None:
        mgr.stop_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        mgr.run()
    finally:
        mgr.close()


if __name__ == "__main__":
    main()
