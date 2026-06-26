# Arginode: Real-Time Offline AI System for Sensor-Integrated Precision Agriculture

Arginode is an end-to-end **offline, sensor-driven agricultural intelligence system** capable of performing real-time soil analysis, crop prediction, fertilizer recommendation, disease risk estimation, and spatial field mapping **without internet dependency**. 

This system integrates multi-sensor hardware (e.g. ESP32/Arduino), machine learning models, and local geospatial analytics to support precision agriculture in remote, connectivity-constrained environments.

---

## 1. System Overview

Traditional digital agriculture solutions rely heavily on cloud connectivity and remote inference infrastructure, making them unsuitable for rural agricultural zones with limited or non-existent network access. Arginode addresses this gap by enabling **fully offline data acquisition, model inference, mapping, and advisory generation**, powered by:

* **Local Machine Learning Inference**: Random Forest models deployed via Scikit-learn and Joblib.
* **Real-Time Sensor Ingestion**: Live NPK (Nitrogen, Phosphorus, Potassium), pH, temperature, and humidity readings streamed from hardware via USB Serial.
* **Geospatial Location Lookup**: Offline state-boundary detection mapping GPS coordinates to states in India using local GeoJSON polygon calculations.
* **Empirical Fertilizer Advisor**: Dataset-driven recommendations based on nearest-neighbor feature search matching current readings with empirical training samples.
* **Dynamic Local Dashboard**: A React frontend rendering real-time telemetry, historical prediction logs, spatial charts, and interactive map layers.

---

## 2. Core Architecture

```
┌─────────────────┐  USB/Serial  ┌───────────────────────┐
│ Arduino / ESP32 │ ────────────▶│ scripts/ingest_arduino│
│ (NPK + pH + GPS)│              │ Ingestion Script      │
└─────────────────┘              └───────────────────────┘
                                             │ POST /ingest (JSON)
                                             ▼
                                 ┌───────────────────────┐
                                 │ FastAPI Backend       │
                                 │ - Scikit-Learn Models │
                                 │ - Geospatial Resolver │
                                 │ - JSON History DB     │
                                 └───────────────────────┘
                                             │
                                             │ WebSockets / JSON
                                             ▼
                                 ┌───────────────────────┐
                                 │ React Frontend UI     │
                                 │ - Real-time Feed      │
                                 │ - Interactive Maps    │
                                 │ - Historical Data     │
                                 └───────────────────────┘
```

---

## 3. Project Directory Structure

```
offline-precision-agriculture-ai/
├── core_utils/                 # Shared utilities and helpers
├── data/                       # Dataset files and geojson boundary data
│   ├── arginode_corrected_fertilizers.csv  # Combined training dataset
│   ├── india_states.geojson    # Geographic boundaries of Indian states
│   └── india_min.geojson       # Simplified geojson for faster rendering
├── db/                         # Database storage directory
├── frontend/                   # React web application
│   ├── public/                 # Static assets
│   ├── src/                    # React components and styling
│   └── package.json            # React project dependencies
├── models/                     # Trained ML models (ignored in git)
├── scripts/                    # Ingestion and helper scripts
│   └── ingest_arduino.py       # Serial ingest connector script
├── server/                     # FastAPI backend
│   ├── main.py                 # Main FastAPI router & websocket hub
│   ├── geo_resolver.py         # Geospatial coordinate to state resolver
│   ├── models_loader.py        # Model loading utilities
│   ├── fertilizer_recommender_csv.py # Nearest neighbor recommendation engine
│   └── history.json            # Local JSON prediction history database
├── requirements.txt            # Python dependencies
├── start_project.ps1           # Windows PowerShell automated launcher
├── train_crop_model.py         # Model training script
└── find_esp32.py               # Serial port autodiscovery helper
```

---

## 4. Features & Interfaces

### 4.1 Real-Time Live Sensor Feed
* Ingestion of raw serial sensor packets.
* Exponential moving average buffering to prevent noise/erroneous recommendations.
* WebSockets connection for live telemetry updates in the web dashboard.
* Control toggles to pause/resume the feed dynamically.

### 4.2 Offline Prediction Engine
* Classification model trained to predict optimal crops based on soil and environmental features:
  * Nitrogen (N), Phosphorus (P), Potassium (K)
  * Soil pH
  * Temperature (°C)
  * Humidity (%)
  * Annual Rainfall (mm)

### 4.3 Nearest-Neighbor Fertilizer Recommender
* Calculates the Euclidean distance ($L_2$ norm) across feature spaces between live readings and the empirical crop-dataset.
* Retrieves matching historical records to determine exact, location-appropriate fertilizer recommendations rather than static threshold rules.

### 4.4 Local Geospatial Resolution
* Coordinates (Latitude, Longitude) are resolved to regional state boundaries using ray-casting algorithms against local GeoJSON boundaries without needing Google Maps or other cloud services.

---

## 5. Hardware Interface Specifications

The ingestion script (`scripts/ingest_arduino.py`) listens to the active USB Serial port (baud rate `9600`) and expects incoming messages formatted in structured frames:

```text
*start*
*n:45
*p:32
*k:60
*ph:6.5
*t:28.4
*h:62.0
*la:17.3871
*lo:78.4821
```

* **Keys Mapper**:
  * `n`: Nitrogen value
  * `p`: Phosphorus value
  * `k`: Potassium value
  * `ph`: Soil pH
  * `t`: Temperature (°C)
  * `h`: Humidity (%)
  * `la`: Latitude
  * `lo`: Longitude

The ingestion script packages these readings into a JSON payload and issues a `POST` request to `/ingest`.

---

## 6. API Endpoints

### 6.1 HTTP REST Endpoints

#### `POST /ingest`
Receives live telemetry payloads from the serial script.
* **Payload**:
  ```json
  {
    "N": 45.0, "P": 32.0, "K": 60.0,
    "pH": 6.5, "temperature": 28.4, "humidity": 62.0,
    "rainfall": 0.0, "latitude": 17.3871, "longitude": 78.4821
  }
  ```

#### `POST /manual_predict`
Performs an on-demand prediction from manually inputted values in the dashboard UI and saves the prediction to the history log.

#### `GET /history`
Retrieves all historical runs from `server/history.json`.

#### `DELETE /history`
Clears the prediction history logs.

#### `GET /geojson`
Loads and returns the local GeoJSON state boundaries map.

#### `POST /toggle_pause`
Pauses or resumes telemetry processing.

### 6.2 WebSocket Endpoints

#### `WS /ws/live`
WebSocket stream broadcasting updated live predictions to all connected dashboard frontend clients.

---

## 7. Setup & Run Instructions

### 7.1 Automated Start (Windows)
Run the PowerShell launcher script, which automatically checks for Python/Node, creates virtual environments, installs dependencies, autodetects connected ESP32/Arduino microcontrollers, and runs all processes:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start_project.ps1
```

### 7.2 Manual Installation

#### 1. Clone the repository
```bash
git clone https://github.com/DragonBlade431/arginode.git
cd arginode
```

#### 2. Setup Python environment & backend
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Train models
Make sure to train the machine learning models before starting the server so the backend can load the pipeline:
```bash
python train_crop_model.py
```

#### 4. Run Backend Server
```bash
uvicorn server.main:app --reload --port 8000
```

#### 5. Setup & Start Frontend
Open a new terminal window:
```bash
cd frontend
npm install
npm start
```

#### 6. Run Arduino Serial Ingestion
Connect your ESP32/Arduino via USB, check the COM port, and run:
```bash
python scripts/ingest_arduino.py --port "COM3"  # or "/dev/tty.usbserial-XXXX" on macOS/Linux
```

---

## 8. Dataset Details

The dataset `data/arginode_corrected_fertilizers.csv` compiles empirical readings including:
* Nitrogen, Phosphorus, Potassium (N, P, K) ratios
* Soil pH and moisture profiles
* Temperature and rainfall records
* Coordinate state mappings
* Target Crop & Fertilizer Recommendations

The recommendation system calculates nearest-neighbor parameters against this dataset to provide real-time agricultural advisories.
