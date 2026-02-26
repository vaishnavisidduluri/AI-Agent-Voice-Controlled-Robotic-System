# Project Setup & Installation Guide

This document explains how to set up and run the **Agentic AI Voice-Controlled Robotic Arm** on both **Linux VM** and **Raspberry Pi**.

---

## 1. System Requirements

### Hardware

- Raspberry Pi 4 (4GB or higher recommended)
- External power supply (5–6V, 5–10A)
- Robotic arm with servo motors
- USB camera and microphone

### Software

- Python 3.9+
- Raspberry Pi OS (for deployment)
- Ubuntu Linux (VM for development)

---

## 2. Linux VM Setup (Development)

### Step 1: Update system

```bash
sudo apt update && sudo apt upgrade
```

### Step 2: Install Python & tools

```bash
sudo apt install python3 python3-pip git
```

### Step 3: Clone repository

```bash
git clone <project-repo-url>
cd agentic-robotic-arm
```

### Step 4: Install dependencies

```bash
pip3 install -r requirements.txt
```

### Step 5: Test perception modules

```bash
python scripts/test_camera.py
python scripts/test_microphone.py
```

Hardware-specific modules will be mocked in this environment.

## 3. Raspberry Pi Setup (Deployment)

### Step 1: Install Raspberry Pi OS

Flash Raspberry Pi OS using Raspberry Pi Imager

Enable:

SSH

I2C

Camera interface

### Step 2: System update

```bash
sudo apt update && sudo apt upgrade
```

### Step 3: Install dependencies

```bash
sudo apt install python3-pip i2c-tools
pip3 install -r requirements.txt
```

### Step 4: Verify I2C

```bash
i2cdetect -y 1
```

PCA9685 should be visible.

## 4. Hardware Connection Check

Ensure common ground between Raspberry Pi and servo power

Verify servo channels

Check camera and microphone detection

## 5. Running the System

Start the main system

```bash
python scripts/start_system.py
```

Servo calibration (first time only)

```bash
python scripts/calibrate_servos.py
```

## 6. Testing & Debugging

Logs stored in logs/

Test individual agents using unit tests

Use simulation modules before hardware execution

## Safety Notes

Never power servos directly from Raspberry Pi

Always set joint angle limits

Test movements at low speed first
