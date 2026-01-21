# gpio.py
"""
Deprecated GPIO helper (v2.0 transitional).

Currently used only for STM32 NRST reset via Raspberry Pi GPIO.
All motor/servo control has moved to STM32 via SPI.
"""

import mmap
import os
import struct
import time
from . import _spi_bus

# ================== Configuration ==================
# BCM pin connected to STM32 NRST
NRST_GPIO = 23          # BCM numbering
RESET_PULSE = 0.05      # Reset low time (seconds)
# ===================================================

# Raspberry Pi 4/5 GPIO base
GPIO_BASE = 0xFE200000
GPIO_LEN  = 0xF4

# GPIO register offsets
GPFSEL0 = 0x00
GPFSEL1 = 0x04
GPFSEL2 = 0x08
GPSET0  = 0x1C
GPCLR0  = 0x28


# ------------------ Low-level helpers ------------------

def _gpio_set_output(mem, pin: int) -> None:
    reg = GPFSEL0 + (pin // 10) * 4
    shift = (pin % 10) * 3

    val = struct.unpack("I", mem[reg:reg + 4])[0]
    val &= ~(0b111 << shift)     # clear
    val |=  (0b001 << shift)     # output
    mem[reg:reg + 4] = struct.pack("I", val)


def _gpio_set_input(mem, pin: int) -> None:
    """Release NRST line (High-Z)."""
    reg = GPFSEL0 + (pin // 10) * 4
    shift = (pin % 10) * 3

    val = struct.unpack("I", mem[reg:reg + 4])[0]
    val &= ~(0b111 << shift)     # INPUT (000)
    mem[reg:reg + 4] = struct.pack("I", val)


def _gpio_high(mem, pin: int) -> None:
    mem[GPSET0:GPSET0 + 4] = struct.pack("I", 1 << pin)


def _gpio_low(mem, pin: int) -> None:
    mem[GPCLR0:GPCLR0 + 4] = struct.pack("I", 1 << pin)


# ------------------ Public API ------------------

def reset() -> None:
    """Hardware reset for STM32 via NRST GPIO.

    This function asserts NRST low, then releases it and finally
    switches the pin to INPUT (High-Z) so STM32 internal pull-up
    takes over.

    Usage:
        >>> import afb.gpio
        >>> afb.gpio.reset()
    """
    fd = None
    mem = None

    try:
        fd = os.open("/dev/gpiomem", os.O_RDWR | os.O_SYNC)
        mem = mmap.mmap(
            fd,
            GPIO_LEN,
            mmap.MAP_SHARED,
            mmap.PROT_READ | mmap.PROT_WRITE,
            offset=0
        )

        # 1) Configure as output
        _gpio_set_output(mem, NRST_GPIO)

        # 2) Idle high
        _gpio_high(mem, NRST_GPIO)
        time.sleep(0.05)

        # 3) Assert reset (LOW)
        _gpio_low(mem, NRST_GPIO)
        time.sleep(RESET_PULSE)

        # 4) Release reset (HIGH)
        _gpio_high(mem, NRST_GPIO)
        time.sleep(0.01)

        # 5) Release NRST line (High-Z)
        _gpio_set_input(mem, NRST_GPIO)

    finally:
        if mem is not None:
            mem.close()
        if fd is not None:
            os.close(fd)


def getMode():
    """Deprecated. GPIO-based mode detection is no longer used."""
    _spi_bus.get_mode()
    time.sleep(float(0.005))
    rx=_spi_bus.status_request()
    
    return rx

def stm_release():
    _spi_bus.close()