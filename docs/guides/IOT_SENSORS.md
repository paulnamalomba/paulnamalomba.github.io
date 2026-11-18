# IoT sensors deep dive: Analog-to-Digital, protocols, and backhaul

<br>
Last updated: February 26, 2026<br>
Author: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
Contact: [kabwenzenamalomba@gmail.com](mailto:kabwenzenamalomba@gmail.com)<br>
Website: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>
[![Hardware](https://img.shields.io/badge/Hardware-Edge_Compute-orange.svg)](https://learn.microsoft.com/en-us/azure/iot-edge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This guide follows IoT sensor data through hardware acquisition, network transport, and cloud ETL pipelines. It covers analog-to-digital conversion (ADC), MQTT and HTTP telemetry, internet backhaul, and large-scale data tunneling.

## Contents

- [IoT sensors deep dive: Analog-to-Digital, protocols, and backhaul](#iot-sensors-deep-dive-analog-to-digital-protocols-and-backhaul)
  - [Overview](#overview)
  - [Contents](#contents)
  - [1. Configuration (Windows \& Linux)](#1-configuration-windows--linux)
    - [Linux (Debian/Ubuntu) strategy](#linux-debianubuntu-strategy)
    - [Windows strategy](#windows-strategy)
  - [2. Writing basic Code/scripts (ADC \& telemetry)](#2-writing-basic-codescripts-adc--telemetry)
    - [Analog-to-Digital conversion (ADC)](#analog-to-digital-conversion-adc)
    - [Network protocols: MQTT vs. HTTP](#network-protocols-mqtt-vs-http)
  - [3. Compile-time commands (firmware generation)](#3-compile-time-commands-firmware-generation)
  - [4. Runtime commands (daemonization \& ETL backhaul)](#4-runtime-commands-daemonization--etl-backhaul)
    - [Internet backhaul](#internet-backhaul)
    - [Tunneling data streams into ETL pipelines](#tunneling-data-streams-into-etl-pipelines)
  - [5. Debugging (radio silence \& data loss)](#5-debugging-radio-silence--data-loss)
    - [Edge debugging](#edge-debugging)
    - [Backhaul debugging](#backhaul-debugging)

---

## 1. Configuration (Windows & Linux)

Setting up an IoT development environment requires configuring toolchains capable of cross-compiling code for embedded architectures (ARM, ESP32, AVR).

### Linux (Debian/Ubuntu) strategy

Linux provides the most predictable environment for embedded toolchains and serial communication.

```bash
# Install the GCC ARM cross-compiler and essential build tools
sudo apt update && sudo apt install -y build-essential gcc-arm-none-eabi

# Add user to the dialout group to allow flashing over USB/Serial
sudo usermod -a -G dialout $USER

# Install Python packages required by most modern build systems (like PlatformIO or Espressif IDF)
pip3 install pyserial platformio
```

### Windows strategy

Windows development requires strict path management and driver installations (usually CP210x or CH340 for USB-to-UART bridges). Toolchains are best managed via PlatformIO within VS Code to bypass native environment pathing nightmares.

**Key Config Files:**

- `/etc/udev/rules.d/`: On Linux, defining udev rules ensures predictable mounting of serial devices (e.g., mapping a specific sensor to `/dev/ttySensor`).
- `platformio.ini`: The central configuration file for modern embedded projects, specifying the target board, framework (Arduino vs. ESP-IDF), upload ports, and baud rates.

---

## 2. Writing basic Code/scripts (ADC & telemetry)

The code lifecycle of an edge sensor dictates reading raw analog voltage, converting it to a discrete digital value via an ADC, synthesizing a payload, and pushing it out via a network protocol like MQTT or HTTP.

### Analog-to-Digital conversion (ADC)

An ADC maps continuous voltage variations to discrete integer values based on its bit resolution (e.g., a 12-bit ADC provides 4096 discrete steps).

```cpp
#include <Arduino.h>

#define SENSOR_PIN 34  // Analog pin
#define ADC_RESOLUTION 4095.0 // 12-bit ADC
#define V_REF 3.3      // Reference voltage

void setup() {
    Serial.begin(115200);
    analogReadResolution(12); // Enforce 12-bit resolution
}

void loop() {
    int rawValue = analogRead(SENSOR_PIN);
    // Convert raw integer back into a physical voltage
    float voltage = (rawValue / ADC_RESOLUTION) * V_REF;

    // Derived physical metric calculation (e.g., Temperature mapping)
    float temperatureC = (voltage - 0.5) * 100.0;

    Serial.printf("Raw: %d, Volts: %.2fV, Temp: %.2f°C\n", rawValue, voltage, temperatureC);
    delay(2000);
}
```

### Network protocols: MQTT vs. HTTP

While HTTP requires significant overhead via headers and establishing new TCP sockets per request, **MQTT is the industry standard for IoT**. MQTT maintains a persistent, lightweight TCP connection to a broker, publishing tiny packets asynchronously on defined "topics."

```python
import paho.mqtt.client as mqtt
import json

BROKER = "mqtt.enterprise.internal"
CLIENT_ID = "Sensor_A1"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to backhaul with result code {rc}")

client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.connect(BROKER, 1883, 60)

# Tunneling payload
payload = json.dumps({
    "device_id": CLIENT_ID,
    "temperature": 24.5,
    "timestamp": 1709088421
})

# Publish to topic with Quality of Service (QoS) 1 (At least once delivery)
client.publish("telemetry/facility1/hvac", payload, qos=1)
client.loop_start()
```

---

## 3. Compile-time commands (firmware generation)

Microcontrollers do not possess a runtime engine capable of interpreting raw source code. The code must be compiled, linked, and assembled into a `.bin` or `.hex` binary payload specific to the target silicon architecture.

Using PlatformIO:

```bash
# Clean previous build artifacts
pio run --target clean

# Compile the firmware for the target defined in platformio.ini
pio run

# Compile and upload over the serial port to the physical hardware
pio run --target upload
```

_Pre-execution analysis:_ The compiler performs strict static typing and memory allocation checks. Because microcontrollers possess kilobytes (not gigabytes) of RAM, dynamic allocation (`malloc` or `new`) is highly discouraged. The compiler generates memory maps indicating `.bss` and `.data` segment usage to prevent stack collisions.

---

## 4. Runtime commands (daemonization & ETL backhaul)

While the edge devices execute firmware continuously in an infinite `loop()`, the receiving end—the telemetry backhaul—must daemonize its ingestion services to catch the datastream without interruption.

### Internet backhaul

Managing large volumes of telemetry from edge gateways requires queueing systems. Services like Mosquitto (MQTT Broker) must run reliably under the system supervisor.

```bash
# Enable the MQTT broker daemon on Ubuntu
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Check ingestion bandwidth
netstat -tulpn | grep 1883
```

### Tunneling data streams into ETL pipelines

Once telemetry reaches the broker, a subscriber daemon immediately extracts, transforms, and loads (ETL) it into a timeseries database (like TimescaleDB or InfluxDB).

```bash
# Running an ingestion worker script as a background daemon
nohup python3 /opt/telemetry/ingestion_worker.py > /var/log/iot/ingestion.log 2>&1 &

# Better approach: Establish a Systemd Service for the ETL worker
# /etc/systemd/system/etl-worker.service
```

---

## 5. Debugging (radio silence & data loss)

Because hardware fails without throwing stack traces to a terminal, debugging IoT infrastructure relies heavily on signal persistence tools and log aggregation. Nothing builds character quite like deciphering why an I2C bus locked up purely because a pull-up resistor was rated 1k Ohm instead of 4.7k Ohm.

### Edge debugging

- **Serial Monitors:** Hooking a USB cable directly to the UART bridge is your primary window into the microcontroller.
  ```bash
  pio device monitor --baud 115200
  ```
- **Common Pitfalls:** Ground loops introducing analog noise to the ADC, resulting in erratic sensor readings. Always tie sensor grounds directly to the microcontroller logic ground.

### Backhaul debugging

- **Topic Snooping:** Subscribe to the wildcard topic `#` to verify data is actually hitting the network layer.
  ```bash
  mosquitto_sub -h localhost -t "#" -v
  ```
- **Log Check:** Tracebacks indicating connection drops (`EOF` or TCP timeouts) generally indicate poor signal strength at the edge or excessively aggressive keep-alive timers.
  ```bash
  tail -f /var/log/mosquitto/mosquitto.log
  ```
