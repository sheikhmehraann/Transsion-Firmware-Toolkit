#!/usr/bin/env bash
# Transsion Fastboot Multi-Partition Flasher for Linux / macOS / WSL
set -e

echo "==================================================================="
echo "              TRANSSION FASTBOOT FIRMWARE FLASHER"
echo "           (Helio G99 MT6789 / Dimensity 8200/8300/9000)"
echo "==================================================================="

fastboot devices

echo "[*] Flashing Critical Bootloader Partitions..."
[ -f "boot.img" ] && fastboot flash boot boot.img
[ -f "init_boot.img" ] && fastboot flash init_boot init_boot.img
[ -f "vendor_boot.img" ] && fastboot flash vendor_boot vendor_boot.img
[ -f "dtbo.img" ] && fastboot flash dtbo dtbo.img
[ -f "vbmeta.img" ] && fastboot flash vbmeta --disable-verity --disable-verification vbmeta.img
[ -f "vbmeta_vendor.img" ] && fastboot flash vbmeta_vendor vbmeta_vendor.img
[ -f "vbmeta_system.img" ] && fastboot flash vbmeta_system vbmeta_system.img

echo "[*] Rebooting into Fastbootd..."
fastboot reboot fastboot

echo "[*] Flashing Logical Super Partitions..."
[ -f "system.img" ] && fastboot flash system system.img
[ -f "vendor.img" ] && fastboot flash vendor vendor.img
[ -f "product.img" ] && fastboot flash product product.img
[ -f "system_ext.img" ] && fastboot flash system_ext system_ext.img
[ -f "odm.img" ] && fastboot flash odm odm.img

echo "[✓] Flashing complete! Rebooting..."
fastboot reboot
