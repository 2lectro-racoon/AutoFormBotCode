#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# ========= 사용자 설정 =========
OPENOCD = "openocd"

# 스크립트 위치 기준 경로
SCRIPT_DIR = Path(__file__).resolve().parent                 # .../AutoFormBotCode/scripts/firmware
SCRIPTS_DIR = SCRIPT_DIR.parent                              # .../AutoFormBotCode/scripts
REPO_ROOT = SCRIPTS_DIR.parent                               # .../AutoFormBotCode
DEFAULT_FW_DIR = REPO_ROOT / "firmware"                      # .../AutoFormBotCode/firmware

# 있으면 이 파일 사용 (핀 고정)
CUSTOM_IF_CFG = SCRIPT_DIR / "rpi_swd.cfg"

# 없으면 기본 설정 사용 (OpenOCD 내장 cfg)
DEFAULT_IF_CFG = "interface/raspberrypi-swd.cfg"

TARGET_CFG = "target/stm32f1x.cfg"
FLASH_ADDR = "0x08000000"
# ===============================


def run(cmd: list[str]) -> None:
    print("\n[RUN]")
    print(" ".join(cmd))
    print("-" * 60)

    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    print(p.stdout)

    if p.returncode != 0:
        print("[ERROR] OpenOCD failed")
        sys.exit(1)


def resolve_firmware_path(arg: str | None) -> Path:
    """펌웨어 경로 해석.

    - 인자를 주면: 절대경로/상대경로 모두 허용
    - 인자를 안 주면: ~/AutoFormBotCode/firmware/firmware.bin 기본
    - 인자가 파일명만이면: DEFAULT_FW_DIR 아래에서 찾음
    """
    if not arg:
        candidate = DEFAULT_FW_DIR / "firmware.bin"
        return candidate

    p = Path(arg).expanduser()

    # 절대경로/상대경로로 실제 파일이 있으면 그대로
    if p.exists():
        return p

    # 파일명만 준 경우: 기본 firmware 폴더에서 탐색
    candidate = DEFAULT_FW_DIR / p.name
    return candidate


def main() -> None:
    # 사용법: 인자 생략 시 기본 펌웨어 경로 사용
    if len(sys.argv) > 2:
        print("Usage:")
        print("  python3 flash.py [firmware.bin]")
        print(f"  (default: {DEFAULT_FW_DIR}/firmware.bin)")
        sys.exit(1)

    fw_arg = sys.argv[1] if len(sys.argv) == 2 else None
    bin_path = resolve_firmware_path(fw_arg)

    if not bin_path.exists():
        print(f"[ERROR] File not found: {bin_path}")
        print("[HINT] Put firmware at:")
        print(f"       {DEFAULT_FW_DIR}/firmware.bin")
        sys.exit(1)

    # interface cfg 선택 (스크립트 폴더에 rpi_swd.cfg가 있으면 그걸 우선)
    if_cfg = str(CUSTOM_IF_CFG) if CUSTOM_IF_CFG.exists() else DEFAULT_IF_CFG

    print("[INFO] Script dir :", SCRIPT_DIR)
    print("[INFO] Repo root  :", REPO_ROOT)
    print("[INFO] Using interface config:", if_cfg)
    print("[INFO] Firmware:", bin_path)
    print("[INFO] Note: This script does NOT issue 'reset halt/run' to avoid NRST(mmap) conflicts.")

    cmd = [
        OPENOCD,
        "-f",
        if_cfg,
        "-c",
        "transport select swd",
        "-f",
        TARGET_CFG,
        "-c",
        "init",
        "-c",
        f"flash write_image erase {bin_path} {FLASH_ADDR}",
        "-c",
        f"verify_image {bin_path} {FLASH_ADDR}",
        "-c",
        "exit",
    ]

    run(cmd)

    print("[OK] Flash completed successfully")
    print("[INFO] If your board needs a reset to start the new firmware, toggle NRST via your GPIO reset script.")


if __name__ == "__main__":
    main()