@echo off
title Transsion Fastboot Multi-Partition Flasher
color 0B

echo ===================================================================
echo               TRANSSION FASTBOOT FIRMWARE FLASHER
echo            (Helio G99 MT6789 / Dimensity 8200/8300/9000)
echo ===================================================================
echo.

fastboot devices
if errorlevel 1 (
    echo [ERROR] No Fastboot device detected! Connect device via USB.
    pause
    exit /b 1
)

echo [*] Flashing Critical Bootloader Partitions...
if exist boot.img fastboot flash boot boot.img
if exist init_boot.img fastboot flash init_boot init_boot.img
if exist vendor_boot.img fastboot flash vendor_boot vendor_boot.img
if exist dtbo.img fastboot flash dtbo dtbo.img
if exist vbmeta.img fastboot flash vbmeta --disable-verity --disable-verification vbmeta.img
if exist vbmeta_vendor.img fastboot flash vbmeta_vendor vbmeta_vendor.img
if exist vbmeta_system.img fastboot flash vbmeta_system vbmeta_system.img

echo.
echo [*] Entering Fastbootd for Dynamic Partitions...
fastboot reboot fastboot

echo [*] Flashing Logical Super Partitions...
if exist system.img fastboot flash system system.img
if exist vendor.img fastboot flash vendor vendor.img
if exist product.img fastboot flash product product.img
if exist system_ext.img fastboot flash system_ext system_ext.img
if exist odm.img fastboot flash odm odm.img

echo.
echo [✓] Flashing Complete! Rebooting to System...
fastboot reboot
pause
