# Transsion Firmware Toolkit 🚀

[![CI & Tests](https://github.com/sheikhmehraann/Transsion-Firmware-Toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/sheikhmehraann/Transsion-Firmware-Toolkit/actions)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Zstandard: -19](https://img.shields.io/badge/Zstandard-Level%2019-orange.svg)](https://facebook.github.io/zstd/)

> **The Ultimate All-in-One Firmware & OTA Toolkit for Transsion (Infinix, TECNO, itel) & MediaTek Android Devices.**
> 
> *Dedicated to and honoring the pioneering reverse engineering work of **Rama Bondan Prakoso** ([@ramabondanp](https://github.com/ramabondanp) / [`rama982`](https://forum.xda-developers.com/m/rama982.9099884/)).*

---

## 📖 Overview

The **Transsion Firmware Toolkit** provides a complete, unified suite for probing, downloading, extracting, reconstructing, patching, and flashing firmware for Android smartphones produced by Transsion Holdings (**Infinix**, **TECNO**, **itel**) and MediaTek chipsets (Helio G80/G95/G99 and Dimensity 8200/8300/9000).

It brings together Rama Bondan Prakoso's reverse-engineered protocols and tools into one streamlined CLI and automation framework:

1. 🔍 **Protobuf OTA Prober**: Query official FOTA / Google Check-in servers for new incremental or full firmware `.zip` update links.
2. 📦 **Full & Incremental Payload Extraction**: Extract raw partition `.img` files from `payload.bin`, and reconstruct byte-accurate updated images from incremental delta diffs.
3. 🗜️ **Rama-Style `.tar.zst` Packager**: Generate high-ratio, ultra-fast decompressing `X6871-...-images.tar.zst` packages matching official releases on SourceForge.
4. ⚡ **Multi-Partition Fastboot Flasher**: Cross-platform flash engine supporting logical dynamic super partitions (`system`, `vendor`, `product`, `odm`) in `fastbootd`.
5. 🛠️ **64-Bit Vendor Converter**: Automatically convert 32/64-bit hybrid Transsion vendor trees to pure 64-bit only (`arm64-v8a`) to eliminate bootloops on Generic System Images (GSI).
6. ☁️ **Automated GitHub Actions Cloud Extractor**: Provide an OTA URL and let GitHub Actions extract and release the compressed partition images in the cloud.

---

## 🛠️ Architecture & Workflow

```mermaid
flowchart LR
    A[Transsion FOTA / Google Checkin] -->|OTA Prober| B[Direct Update ZIP URL]
    B -->|Payload Dumper| C{Full or Incremental?}
    C -->|Full OTA| D[Extract All .img Partitions]
    C -->|Incremental Delta| E[Apply BSDIFF / PUFFIN against Source Images]
    E --> D
    D -->|Zstandard Level 19| F[X6871-...-images.tar.zst]
    F -->|Fastboot Multi-Flasher| G[Target Device Hardware]
```

---

## 📱 Hardware & Target Devices Supported

| Brand | Model Codename | Market Name | Chipset Platform |
| :--- | :--- | :--- | :--- |
| **Infinix** | `X6871` / `X6871B` | **Infinix GT 20 Pro** | MediaTek Dimensity 8200 Ultimate |
| **Infinix** | `X6739` | **Infinix GT 10 Pro** | MediaTek Dimensity 8050 |
| **Infinix** | `X6833B` | **Infinix Note 30 VIP** | MediaTek Dimensity 8050 |
| **Infinix** | `X6711` | **Infinix Note 40 Pro+ 5G** | MediaTek Dimensity 7020 |
| **Infinix** | `X695C` | **Infinix Note 10 Pro (ID)** | MediaTek Helio G95 |
| **Infinix** | `X6815` | **Infinix Zero 5G** | MediaTek Dimensity 900 |
| **TECNO** | `KJ7` | **TECNO Spark 20 Pro+** | MediaTek Helio G99 Ultimate |
| **TECNO** | `LH8n` | **TECNO Pova 5 Pro 5G** | MediaTek Dimensity 6080 |
| **TECNO** | `CK7n` | **TECNO Camon 20 Pro 5G** | MediaTek Dimensity 8050 |
| **TECNO** | `AD10` | **TECNO Phantom V Fold** | MediaTek Dimensity 9000+ |

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/sheikhmehraann/Transsion-Firmware-Toolkit.git
cd Transsion-Firmware-Toolkit

# Install dependencies
pip install -r requirements.txt
```

### Optional Native Dependencies:
- `zstd` (for CLI compression)
- `fastboot` / `adb` (Android Platform Tools)
- `payload-dumper-go` (optional native high-speed binary)

---

## 💻 Usage & Commands

### 1. View Supported Devices
```bash
python main.py devices
```

### 2. Probe OTA Updates for a Device
```bash
# Probe updates for Infinix GT 20 Pro
python main.py probe -m X6871

# Probe updates for Tecno Spark 20 Pro+
python main.py probe -m KJ7
```

### 3. Extract Full OTA Package
```bash
# Extract partition images from OTA .zip
python main.py extract ota_update.zip -o ./extracted_images/

# Or directly from payload.bin
python main.py extract payload.bin -o ./extracted_images/
```

### 4. Reconstruct Incremental OTA Updates
```bash
# Apply incremental payload deltas against base images from previous firmware
python main.py reconstruct payload.bin -s ./source_images_v1/ -o ./target_images_v2/
```

### 5. Pack Images into Rama-Style `.tar.zst`
```bash
# Compress extracted partition images into high-ratio Zstandard tarball
python main.py pack ./extracted_images/ -o X6871-15.1.2.180SP05-OP001PF001AZ-images.tar.zst -l 19
```

### 6. Decompress `.tar.zst` Archive
```bash
python main.py unpack X6871-15.1.2.180SP05-OP001PF001AZ-images.tar.zst -o ./ready_to_flash/
```

### 7. Flash Extracted Firmware via Fastboot
```bash
# Automatically flashes boot partitions, enters fastbootd, and flashes dynamic super partitions
python main.py flash ./ready_to_flash/
```

### 8. Convert Vendor to 64-Bit Only for GSI
```bash
# Strips 32-bit legacy abilist constraints from Transsion vendor trees
python main.py fix-vendor /path/to/mounted_vendor/
```

---

## ⚡ Flashing Guide for Infinix GT 20 Pro (`X6871`)

When flashing custom recoveries or extracted partition packages on the **Infinix GT 20 Pro**:

1. **Flash Recovery / Boot**:
   ```bash
   fastboot flash vendor_boot vendor_boot.img
   fastboot flash boot boot.img
   fastboot flash init_boot init_boot.img
   ```
2. **Important Booting Instruction**:
   > ⚠️ **DO NOT run `fastboot reboot recovery`!** 
   > Instead, power down the device and hold **Power + Volume Up** physically to trigger recovery mode.

---

## 🤝 Credits & Acknowledgements

- **Rama Bondan Prakoso** ([@ramabondanp](https://github.com/ramabondanp) / [`rama982`](https://forum.xda-developers.com/m/rama982.9099884/)): For pioneering Transsion OTA probing, Genom Kernel, MT6789 flasher scripts, and 64-bit vendor porting guides.
- **AOSP / update_engine team**: For delta generator and payload specifications.
- **TrebleDroid / phhusson**: For generic system image and vendor hardware overlays.

---

## 📄 License

Licensed under the **Apache License, Version 2.0**. See the [`LICENSE`](LICENSE) file for details.
