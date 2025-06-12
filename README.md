# 🚀 Real-time Multi-robot System with Custom Hardware and Software

This repository contains the implementation details for the Bachelor's thesis, "Development of Custom Hardware and Software for Real-time Multi-robot System," submitted to Metropolia University of Applied Sciences on April 28, 2025. The project focuses on designing a custom I/O board for the Raspberry Pi Compute Module 5 (CM5), a three-port Fast Ethernet switch board, and a Python-based embedded application to enable real-time control of a multi-robot system.

## 📖 Thesis Document

The full thesis document is available at: [https://urn.fi/URN:NBN:fi:amk-2025051411722](https://urn.fi/URN:NBN:fi:amk-2025051411722)

## 📝 Project Overview

The thesis addresses the limitations of the Raspberry Pi 5 for robotic applications by developing tailored hardware and software solutions. Key components include:

- **🔌 Custom CM5 I/O Board**: A compact board with a 5V/5A step-down circuit, optimized I/O ports, and reduced footprint for robotic integration.
- **🌐 Three-port Ethernet Switch Board**: Based on the Microchip KSZ8794, enabling low-latency communication among two robots and a remote control.
- **💻 Embedded Application**: A Python-based system using WebSocket for real-time motor control via a PS4 controller, with pyRTOS for robot-side task scheduling and multithreading for remote control.

The system was validated through hardware and software tests, achieving stable communication (95 Mbps throughput), responsive motor control, and operation within a 15W power budget, despite minor issues with camera flickering and power circuit thermal limits.

### 🔧 Hardware
- Raspberry Pi Compute Module 5 (CM5)
- Custom CM5 I/O board (fabricated using provided schematics)
- Custom three-port Ethernet switch board
- Two BLDC motors with Hall-effect sensors and ESCs
- PS4 controller
- Laptop for remote control
- 24V DC power supply
- Ethernet cables and connectors

### 💾 Software
- Raspberry Pi OS (for CM5)
- Python 3.8+

## 🧪 Testing and Validation

The system was tested for:
- **🔌 Hardware**: Verified functionality of USB, HDMI, Ethernet, MIPI, and GPIO ports. The TPS5450 power circuit was stable at 3A (15W), with minor camera flickering on one MIPI port.
- **💻 Software**: Confirmed accurate motor control with minimal latency using PS4 inputs. WebSocket communication achieved near real-time performance.
- **🌐 Network**: Achieved 95 Mbps throughput and negligible packet loss (0-2 packets over 3600 pings).

## ⚠️ Limitations and Future Work

- **🚫 Limitations**:
  - TPS5450 buck converter overheats at 5A load, limiting power to 3A.
  - Flickering on one MIPI camera port due to potential signal integrity issues.
- **🔮 Future Improvements**:
  - Upgrade to Gigabit Ethernet for multi-camera streaming.
  - Enhance power circuit design for 5A stability.
  - Improve MIPI signal integrity for reliable camera operation.

## ⚖️ License

This project was developed for academic purposes at **Metropolia University of Applied Sciences**. Users can freely use this thesis for educational purpose ONLY.
