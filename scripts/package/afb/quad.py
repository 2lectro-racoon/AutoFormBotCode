# quad.py
"""Quad control API (STM32 firmware: Quad mode).

This module is a thin wrapper around `afb._spi_bus`.
It does NOT open SPI directly; all SPI configuration lives in `_spi_bus.py`.

Public API:
- servo(ch, angle): set each servo angle
- leg(ch, angle0, angle1, angle2): set leg angle

Notes:
"""

from __future__ import annotations

from typing import List

from . import _spi_bus

import time

def servo(ch, angle) -> List[int]:
    return _spi_bus.servo_set(ch, angle)

    


# Motor direction + speed
def leg(ch, a0, a1, a2) ->  None:
    _spi_bus.leg_set(ch, a0, a1,a2)

def legReset() -> None:

    _spi_bus.servo_set(0, 40)
    _spi_bus.servo_set(3, 135)
    _spi_bus.servo_set(6, 40)
    _spi_bus.servo_set(9, 135)
    time.sleep(0.5)
    _spi_bus.servo_set(1, 0)
    _spi_bus.servo_set(4, 180)
    _spi_bus.servo_set(7, 0)
    _spi_bus.servo_set(10, 180)
    time.sleep(0.5)
    _spi_bus.servo_set(2, 180)
    _spi_bus.servo_set(5, 0)
    _spi_bus.servo_set(8, 180)
    _spi_bus.servo_set(11, 0)
    time.sleep(0.5)

    # _spi_bus.leg_set(0, 40, 0, 180)
    # time.sleep(0.5)
    # _spi_bus.leg_set(1, 135, 180, 0)
    # time.sleep(0.5)
    # _spi_bus.leg_set(2, 40, 0, 180)
    # time.sleep(0.5)
    # _spi_bus.leg_set(3, 135, 180, 0)
    # time.sleep(0.5)

def stand() -> None:

    _spi_bus.servo_set(0, 90)
    _spi_bus.servo_set(3, 90)
    _spi_bus.servo_set(6, 90)
    _spi_bus.servo_set(9, 90)
    time.sleep(0.5)
    _spi_bus.servo_set(1, 80)
    _spi_bus.servo_set(4, 100)
    _spi_bus.servo_set(7, 80)
    _spi_bus.servo_set(10, 100)
    time.sleep(0.5)
    _spi_bus.servo_set(2, 90)
    _spi_bus.servo_set(5, 90)
    _spi_bus.servo_set(8, 90)
    _spi_bus.servo_set(11, 90)
    time.sleep(0.5)


    # _spi_bus.leg_set(0, 90, 80, 90)
    # time.sleep(0.5)
    # _spi_bus.leg_set(1, 90, 100, 90)
    # time.sleep(0.5)
    # _spi_bus.leg_set(2, 90, 80, 90)
    # time.sleep(0.5)
    # _spi_bus.leg_set(3, 90, 100, 90)
    # time.sleep(0.5)