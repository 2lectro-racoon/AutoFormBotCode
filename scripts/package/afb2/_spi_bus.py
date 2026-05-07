# _spi_bus.py
"""SPI transport + protocol helper for STM32.

This module centralizes the SPI device configuration and provides
packet build/send helpers for the STM32 firmware.

Packet format (6 bytes):
  [0] 0xAA (header)
  [1] CMD
  [2] LEN (0..2)
  [3] DATA0
  [4] DATA1
  [5] CHECKSUM = CMD ^ LEN ^ DATA0 ^ DATA1 (only for present bytes)

Notes:
- This module does NOT do any interactive I/O.
- Higher-level modules (car.py / quad.py) should call these functions.
"""

from __future__ import annotations

import threading
import time
from typing import Iterable, List, Optional, Sequence

import spidev

# -------------------- SPI config --------------------
SPI_BUS = 0
SPI_DEVICE = 0  # CE0
SPI_MAX_SPEED_HZ = 500_000
SPI_MODE = 0  # SPI_MODE0

# STM32가 SPI 패킷을 파싱할 시간을 확보하기 위한 패킷 간 최소 간격.
# 많은 서보 명령이 연속으로 나갈 때 STM32 수신 파서가 밀리거나 꼬이는 것을 줄인다.
SPI_PACKET_GAP_SEC = 0.0015
# ---------------------------------------------------

_spi: Optional[spidev.SpiDev] = None
_lock = threading.Lock()
_last_packet_t = 0.0


def get_spi() -> spidev.SpiDev:
    """Get (or create) a singleton spidev instance."""
    global _spi
    if _spi is None:
        s = spidev.SpiDev()
        s.open(SPI_BUS, SPI_DEVICE)
        s.max_speed_hz = SPI_MAX_SPEED_HZ
        s.mode = SPI_MODE
        _spi = s
    return _spi


def close() -> None:
    """Close the singleton SPI instance."""
    global _spi
    with _lock:
        if _spi is not None:
            try:
                _spi.close()
            finally:
                _spi = None


# -------------------- Protocol helpers --------------------

def build_packet(cmd: int, data_bytes: Sequence[int] | None = None) -> List[int]:
    """Build a 6-byte packet for STM32."""
    if data_bytes is None:
        data_bytes = []

    length = len(data_bytes)
    if length > 2:
        raise ValueError("data_bytes length must be 0..2")

    cmd &= 0xFF
    length &= 0xFF

    packet = [0xAA, cmd, length, 0, 0, 0]

    checksum = cmd ^ length

    if length > 0:
        b0 = int(data_bytes[0]) & 0xFF
        packet[3] = b0
        checksum ^= b0

    if length > 1:
        b1 = int(data_bytes[1]) & 0xFF
        packet[4] = b1
        checksum ^= b1

    packet[5] = checksum & 0xFF
    return packet


def send_packet(cmd: int, data_bytes: Sequence[int] | None = None) -> List[int]:
    """Send a packet and return the 6-byte response.

    모든 SPI 패킷 전송은 이 함수를 통과한다.
    여기에서 패킷 간 최소 간격을 보장하면 servo_set(), leg_set(), crawl_step()
    어느 경로로 호출되더라도 STM32에 너무 빠르게 명령이 몰리지 않는다.
    """
    global _last_packet_t

    tx = build_packet(cmd, data_bytes)

    with _lock:
        now = time.monotonic()
        remain = SPI_PACKET_GAP_SEC - (now - _last_packet_t)
        if remain > 0:
            time.sleep(remain)

        spi = get_spi()
        rx = spi.xfer2(tx)
        _last_packet_t = time.monotonic()

    # Ensure python list[int]
    return [int(b) & 0xFF for b in rx]


# -------------------- Convenience commands --------------------

def ping() -> List[int]:
    return send_packet(0x0F, [])


def get_mode() -> List[int]:
    """Set firmware mode: 0=CAR, 1=QUAD (per current firmware spec)."""
    return send_packet(0x00, [])


def motor_speed(speed: int) -> List[int]:
    """Set motor speed (-255..255) via CMD 0x01."""
    if speed < -255 or speed > 255:
        raise ValueError("speed must be -255..255")
    data = [speed & 0xFF, (speed >> 8) & 0xFF]
    return send_packet(0x01, data)


def servo_set(ch: int, angle: int) -> List[int]:
    """Set servo channel (0..255) and angle (0..180) via CMD 0x02."""
    if angle < 0 or angle > 180:
        raise ValueError("angle must be 0..180")
    return send_packet(0x02, [ch & 0xFF, angle & 0xFF])


def status_request() -> List[int]:
    """Request status via CMD 0x03."""
    return send_packet(0x03, [])


def leg_set(leg: int, a1: int, a2: int, a3: int, *, sleep_s: float = 0.0) -> None:
    """Set a 3-DOF leg using three servo_set calls.

    Mapping: base_ch = leg * 3, then channels [base_ch+0, base_ch+1, base_ch+2].

    Args:
        leg: leg index (0,1,2,...)
        a1/a2/a3: angles (0..180)
        sleep_s: optional delay between packets (used only if caller wants it)
    """
    import time

    for ang in (a1, a2, a3):
        if ang < 0 or ang > 180:
            raise ValueError("angles must be 0..180")

    base_ch = int(leg) * 3
    angles = [a1, a2, a3]

    for i, ang in enumerate(angles):
        ch = base_ch + i
        servo_set(ch, int(ang))
        if sleep_s > 0:
            time.sleep(float(sleep_s))