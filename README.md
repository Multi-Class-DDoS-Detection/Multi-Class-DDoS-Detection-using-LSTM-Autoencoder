# Multi-Class DDoS Detection Using LSTM Autoencoder and DNN

## Overview

This project presents a complete pipeline for real-time detection and classification of Distributed Denial of Service (DDoS) attacks. It leverages deep learning techniques, combining an LSTM Autoencoder for anomaly detection and a DNN for multi-class attack classification. The solution is based on realistic traffic data and supports real-time deployment scenarios.

![System Outline](Assets/System_outline.png)

---

## Key Features

- **Traffic Simulation**: Simulates various DDoS attack types in a virtualized environment.
- **Traffic Capture**: Utilizes CICFlowMeter for feature extraction from raw network traffic.
- **Two-Phase Detection**:
  - **Phase 1**: LSTM Autoencoder trained on normal traffic to detect anomalies.
  - **Phase 2**: Deep Neural Network (DNN) classifier to identify specific attack types.
- **Real-time Dashboard**: Provides visualizations of traffic patterns, anomalies, and predicted attack classes.
- **Low Latency**: Inference time ~0.28 ms/sample, suitable for high-throughput environments.

---

## Attack Types Covered

The system supports classification of various attack types across different layers:

- **TCP-based Reflection Attacks**: MSSQL
- **UDP/TCP Reflection Attacks**: DNS, PORTMAP, LDAP, NetBIOS, SNMP
- **UDP-based Reflection Attacks**: TFTP, NTP, CharGen
- **TCP Exploitation Attacks**: SYN Flood
- **UDP Exploitation Attacks**: UDP Flood, UDP-Lag

![DDoS Classification](Assets/DDoS_Classification.png)

---

## Dataset

The system is built on the [CIC-DDoS2019](https://www.kaggle.com/datasets/dhoogla/cicddos2019) dataset, which includes labeled flows for a wide range of real-world attack scenarios.

---

## Project Objectives

- Implement an LSTM Autoencoder to detect anomalous network behavior.
- Integrate a DNN classifier for attack-type recognition.
- Minimize false positives and maximize generalization across attack types.
- Support real-time, low-latency detection.
- Enable visualization for practical use in enterprise and academic research environments.

---

## Screenshots


### 📊 Real Time Detection Dashboard
![Dashboard](Assets/DDoS_Detection_Dashboard.png)

The dashboard visualizes network anomaly detection results. It showcases distribution of various DDoS attack types and the proportion of anomalous versus benign traffic. Use also can see the detailed records, enabling effective real-time monitoring and classification of network threats for cybersecurity analysis

---

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multiclass-ddos-detector.git
   cd multiclass-ddos-detector



