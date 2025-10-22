# 🌐 Real-Time Weather Anomaly Detection API

[![API Status](https://img.shields.io/badge/API-Live-brightgreen)](https://real-time-data-profiler.onrender.com/docs)
[![Documentation](https://img.shields.io/badge/Docs-Online-blue)](https://datagems-eosc.github.io/real_time_data_profiler/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **A real-time anomaly detection API service for weather station time series data using sliding window technique.**

Part of the [DataGems EOSC Project](https://github.com/datagems-eosc) - Automatically detects anomalies in temperature, humidity, wind speed, barometric pressure, and rainfall.

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Links](#-quick-links)
- [Quick Start](#-quick-start)
- [API Usage](#-api-usage)
- [Technical Details](#-technical-details)
- [Examples](#-examples)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## ✨ Features

### 🎯 Core Capabilities

- **🕐 Sliding Window Detection**: Configurable window length (W) and stride (S) for time series analysis
- **📊 Multi-Variable Support**: Monitors 5 core meteorological variables simultaneously
- **⚡ Real-Time Processing**: Supports streaming data input with automatic anomaly detection
- **📍 Multi-Station Support**: Simultaneous monitoring of multiple weather stations
- **🔔 Instant Alerts**: Immediate notification when anomalies are detected

### 📈 Monitored Variables

| Variable | Symbol | Unit | Description |
|----------|--------|------|-------------|
| Temperature | `temp_out` | °C | Outdoor temperature |
| Humidity | `out_hum` | % | Outdoor humidity |
| Wind Speed | `wind_speed` | m/s | Wind speed |
| Pressure | `bar` | hPa | Barometric pressure |
| Rainfall | `rain` | mm | Rainfall amount |

---

## 🔗 Quick Links

| Resource | URL | Description |
|----------|-----|-------------|
| **🚀 Live API** | [real-time-data-profiler.onrender.com/docs](https://real-time-data-profiler.onrender.com/docs) | Interactive API documentation (Swagger UI) |
| **📖 User Documentation** | [datagems-eosc.github.io/real_time_data_profiler](https://datagems-eosc.github.io/real_time_data_profiler/) | Complete user guide and examples |
| **🧪 Test Data Endpoint** | [/test-data](https://real-time-data-profiler.onrender.com/test-data) | Get 600 sample observations for testing |
| **🔍 Detection Endpoint** | [/detect](https://real-time-data-profiler.onrender.com/docs#/default/detect_anomalies_detect_post) | POST endpoint for anomaly detection |

---

## 🚀 Quick Start

### Option 1: Use the Live API (No Installation Required)

Visit the interactive API documentation:

```
https://real-time-data-profiler.onrender.com/docs
```

1. Click on **POST /detect**
2. Click **"Try it out"**
3. Click **"Execute"** to test with sample data
4. View the anomaly detection results!

### Option 2: Use via Python

```python
import requests

# API endpoint
url = "https://real-time-data-profiler.onrender.com/detect"

# Prepare your data
data = {
    "observations": [
        {
            "station_id": "574",
            "timestamp": 1729584600,
            "temp_out": 15.2,
            "out_hum": 80.0,
            "wind_speed": 5.5,
            "bar": 1013.2,
            "rain": 0.0
        },
        # Add more observations...
    ],
    "window_len": 10,
    "stride": 1,
    "threshold": 2.5
}

# Send request
response = requests.post(url, json=data)
result = response.json()

# Check results
if result["status"] == "anomalies_found":
    print(f"Found {len(result['anomalies'])} anomalies!")
    for anomaly in result["anomalies"]:
        print(f"  - {anomaly['variable']} at station {anomaly['station_id']}")
else:
    print("No anomalies detected")
```

### Option 3: Run Locally

```bash
# Clone the repository
git clone https://github.com/amy-77/real_time_data_profiler.git
cd real_time_data_profiler/anamoly_detection

# Install dependencies
pip install -r requirements.txt

# Run the API server
python api_server.py

# Access at http://localhost:8000/docs
```

---

## 📡 API Usage

### Endpoint: POST /detect

**URL**: `https://real-time-data-profiler.onrender.com/detect`

#### Request Body

```json
{
  "observations": [
    {
      "station_id": "574",
      "timestamp": 1729584600,
      "temp_out": 15.2,
      "out_hum": 80.0,
      "wind_speed": 5.5,
      "bar": 1013.2,
      "rain": 0.0
    }
  ],
  "window_len": 10,
  "stride": 1,
  "threshold": 2.5
}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `observations` | List[Dict] | **Required** | List of weather observations |
| `window_len` | int | 10 | Sliding window length (≥3) |
| `stride` | int | 1 | Sliding stride (≥1) |
| `threshold` | float | 2.5 | Z-score threshold for anomaly detection |

#### Response (Anomalies Found)

```json
{
  "status": "anomalies_found",
  "message": "Detected 1 anomaly(ies) in the data",
  "total_anomalies": 1,
  "anomalies": [
    {
      "station_id": "574",
      "variable": "temp_out",
      "anomaly_value": 100.0,
      "anomaly_timestamp": "2024-10-22 09:50:00",
      "window_start": "2024-10-22 08:20:00",
      "window_end": "2024-10-22 10:10:00"
    }
  ],
  "detection_params": {
    "window_len": 10,
    "stride": 1,
    "threshold": 2.5,
    "total_observations": 10
  }
}
```

#### Response (No Anomalies)

```json
{
  "status": "no_anomalies",
  "message": "No anomalies detected in the data",
  "total_anomalies": 0,
  "anomalies": [],
  "detection_params": {
    "window_len": 10,
    "stride": 1,
    "threshold": 2.5,
    "total_observations": 10
  }
}
```

---

## 🔬 Technical Details

### Detection Algorithm

The system uses **Z-score based statistical anomaly detection**:

```
Z = (X - μ) / σ

Where:
- X: Current value
- μ: Mean of the time series in the window
- σ: Standard deviation of the time series in the window
```

**Anomaly Criteria**: A value is flagged as anomalous if `|Z| > threshold` (default: 2.5σ)

### Default Configuration

| Parameter | Symbol | Default Value | Meaning |
|-----------|--------|---------------|---------|
| Window Length | W | 36 | 6 hours (36 × 10min) |
| Stride | S | 18 | 3 hours (18 × 10min) |
| Time Interval | Δt | 10 min | Data sampling interval |
| Detection Frequency | - | 3 hours | S × Δt |
| Threshold | σ | 2.5 | Standard deviations |

### Statistical Significance

- **2.5σ threshold**: Corresponds to ~1.2% false positive rate (99% confidence)
- **3.0σ threshold**: Corresponds to ~0.3% false positive rate (99.7% confidence)

---

## 💻 Examples

### Example 1: Basic Detection

```python
import requests

url = "https://real-time-data-profiler.onrender.com/detect"

# Simple test with 5 observations
data = {
    "observations": [
        {"station_id": "S1", "timestamp": 1729584000, "temp_out": 15.0, "out_hum": 80.0, "wind_speed": 5.0, "bar": 1013.0, "rain": 0.0},
        {"station_id": "S1", "timestamp": 1729584600, "temp_out": 15.5, "out_hum": 79.0, "wind_speed": 5.2, "bar": 1013.1, "rain": 0.0},
        {"station_id": "S1", "timestamp": 1729585200, "temp_out": 16.0, "out_hum": 78.0, "wind_speed": 5.5, "bar": 1013.2, "rain": 0.0},
        {"station_id": "S1", "timestamp": 1729585800, "temp_out": 100.0, "out_hum": 77.0, "wind_speed": 5.3, "bar": 1013.0, "rain": 0.0},  # Anomaly!
        {"station_id": "S1", "timestamp": 1729586400, "temp_out": 16.5, "out_hum": 76.0, "wind_speed": 5.1, "bar": 1012.9, "rain": 0.0},
    ],
    "window_len": 5,
    "stride": 1,
    "threshold": 2.5
}

response = requests.post(url, json=data)
print(response.json())
```

### Example 2: Get Test Data

```python
import requests

# Get 600 sample observations
response = requests.get("https://real-time-data-profiler.onrender.com/test-data")
test_data = response.json()

print(f"Received {len(test_data['observations'])} observations")
print(f"Stations: {test_data['metadata']['stations']}")
print(f"Time range: {test_data['metadata']['time_range']}")

# Use test data for detection
detection_response = requests.post(
    "https://real-time-data-profiler.onrender.com/detect",
    json={
        "observations": test_data["observations"][:50],  # Use first 50
        "window_len": 10,
        "stride": 1,
        "threshold": 2.5
    }
)

print(detection_response.json())
```

### Example 3: Multi-Station Monitoring

```python
import requests
from datetime import datetime, timedelta

url = "https://real-time-data-profiler.onrender.com/detect"

# Generate observations for 3 stations
stations = ["S1", "S2", "S3"]
observations = []

base_time = int(datetime.now().timestamp())

for i in range(20):  # 20 time points
    timestamp = base_time + i * 600  # Every 10 minutes
    for station in stations:
        observations.append({
            "station_id": station,
            "timestamp": timestamp,
            "temp_out": 15.0 + i * 0.1,
            "out_hum": 80.0 - i * 0.2,
            "wind_speed": 5.0 + i * 0.05,
            "bar": 1013.0,
            "rain": 0.0
        })

# Detect anomalies
response = requests.post(url, json={
    "observations": observations,
    "window_len": 15,
    "stride": 5,
    "threshold": 2.5
})

result = response.json()
print(f"Status: {result['status']}")
print(f"Total anomalies: {result['total_anomalies']}")

for anomaly in result['anomalies']:
    print(f"  Station {anomaly['station_id']}: {anomaly['variable']} = {anomaly['anomaly_value']}")
```

---

## 🚀 Deployment

### Current Deployment

- **Platform**: [Render.com](https://render.com)
- **URL**: https://real-time-data-profiler.onrender.com
- **Status**: ✅ Live
- **Tier**: Free (may spin down after 15 minutes of inactivity)

### Deploy Your Own Instance

#### Option 1: Deploy to Render

1. Fork this repository
2. Sign up at [render.com](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Set Root Directory: `anamoly_detection`
6. Deploy!

#### Option 2: Deploy to Railway

1. Fork this repository
2. Sign up at [railway.app](https://railway.app)
3. New Project → Deploy from GitHub
4. Select your repository
5. Set Root Directory: `anamoly_detection`
6. Deploy!

#### Option 3: Docker

```bash
# Build image
docker build -t anomaly-detector .

# Run container
docker run -p 8000:8000 anomaly-detector
```

---

## 📊 Project Structure

```
anamoly_detection/
├── api_server.py              # FastAPI application
├── api_test_data.json         # Sample test data (600 observations)
├── requirements.txt           # Python dependencies
├── railway.json               # Railway deployment config
├── runtime.txt                # Python version specification
├── README.md                  # This file
└── docs/
    └── index.html             # User documentation (GitHub Pages)
```

---

## 🛠️ Development

### Local Setup

```bash
# Clone repository
git clone https://github.com/amy-77/real_time_data_profiler.git
cd real_time_data_profiler/anamoly_detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python api_server.py

# Access at http://localhost:8000/docs
```

### Testing

```bash
# Run test script
python test_api.py

# Or use curl
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: application/json" \
  -d @api_test_data.json
```

---

## 📚 Documentation

- **📖 User Guide**: [datagems-eosc.github.io/real_time_data_profiler](https://datagems-eosc.github.io/real_time_data_profiler/)
- **🔧 API Reference**: [real-time-data-profiler.onrender.com/docs](https://real-time-data-profiler.onrender.com/docs)
- **📊 OpenAPI Spec**: [real-time-data-profiler.onrender.com/openapi.json](https://real-time-data-profiler.onrender.com/openapi.json)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is part of the DataGems EOSC Project.

---

## 🙏 Acknowledgments

- **DataGems EOSC Project**: [github.com/datagems-eosc](https://github.com/datagems-eosc)
- **FastAPI**: Modern web framework for building APIs
- **Render.com**: Free hosting platform

---

## 📧 Contact

For questions or support, please open an issue on GitHub or contact the DataGems EOSC team.

---

## 🔖 Version History

- **v1.0.0** (2025-10-22): Initial release
  - Real-time anomaly detection API
  - Support for 5 meteorological variables
  - Sliding window implementation
  - Interactive documentation
  - Public deployment on Render.com

---

**Made with ❤️ by the DataGems EOSC Team**

[![GitHub](https://img.shields.io/badge/GitHub-DataGems--EOSC-blue?logo=github)](https://github.com/datagems-eosc)
[![API](https://img.shields.io/badge/API-Live-brightgreen)](https://real-time-data-profiler.onrender.com/docs)
[![Docs](https://img.shields.io/badge/Docs-Online-blue)](https://datagems-eosc.github.io/real_time_data_profiler/)
