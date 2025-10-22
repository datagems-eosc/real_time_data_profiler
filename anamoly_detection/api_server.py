"""
Real-Time Anomaly Detection API Server
DataGems EOSC Project
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import numpy as np
from collections import defaultdict
from datetime import datetime
import json

app = FastAPI(
    title="Real-Time Data Anomaly Detection API",
    description="Weather Time Series Anomaly Detection Service | DataGems EOSC Project",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class Observation(BaseModel):
    station_id: str = Field(..., description="Weather station ID")
    timestamp: int = Field(..., description="Unix timestamp")
    temp_out: float = Field(..., description="Outdoor temperature (°C)")
    out_hum: float = Field(..., description="Outdoor humidity (%)")
    wind_speed: float = Field(..., description="Wind speed (m/s)")
    bar: float = Field(..., description="Barometric pressure (hPa)")
    rain: float = Field(..., description="Rainfall (mm)")
    
    class Config:
        schema_extra = {
            "example": {
                "station_id": "574",
                "timestamp": 1729580400,
                "temp_out": 15.2,
                "out_hum": 80.0,
                "wind_speed": 5.5,
                "bar": 1013.2,
                "rain": 0.0
            }
        }


class DetectionRequest(BaseModel):
    observations: List[Observation] = Field(..., description="List of observations (user-defined)")
    window_len: int = Field(60, description="Window length W - number of time points (user-defined)", ge=3, le=200)
    stride: int = Field(18, description="Stride S - sliding step (user-defined)", ge=1, le=100)
    threshold: float = Field(2.5, description="Z-score threshold for anomaly detection (user-defined)", ge=1.0, le=5.0)
    
    class Config:
        schema_extra = {
            "example": {
                "observations": [
                    {
                        "station_id": "station_001",
                        "timestamp": 1729580400,
                        "temp_out": 15.2,
                        "out_hum": 80.0,
                        "wind_speed": 5.5,
                        "bar": 1013.2,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729581000,
                        "temp_out": 15.8,
                        "out_hum": 79.0,
                        "wind_speed": 5.2,
                        "bar": 1013.5,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729581600,
                        "temp_out": 16.2,
                        "out_hum": 78.0,
                        "wind_speed": 5.8,
                        "bar": 1013.8,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729582200,
                        "temp_out": 16.5,
                        "out_hum": 77.0,
                        "wind_speed": 6.0,
                        "bar": 1014.0,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729582800,
                        "temp_out": 17.0,
                        "out_hum": 76.0,
                        "wind_speed": 6.2,
                        "bar": 1014.2,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729583400,
                        "temp_out": 100.0,
                        "out_hum": 75.0,
                        "wind_speed": 6.5,
                        "bar": 1014.5,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729584000,
                        "temp_out": 17.8,
                        "out_hum": 74.0,
                        "wind_speed": 6.8,
                        "bar": 1014.8,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729584600,
                        "temp_out": 18.2,
                        "out_hum": 73.0,
                        "wind_speed": 7.0,
                        "bar": 1015.0,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729585200,
                        "temp_out": 18.5,
                        "out_hum": 72.0,
                        "wind_speed": 7.2,
                        "bar": 1015.2,
                        "rain": 0.0
                    },
                    {
                        "station_id": "station_001",
                        "timestamp": 1729585800,
                        "temp_out": 19.0,
                        "out_hum": 71.0,
                        "wind_speed": 7.5,
                        "bar": 1015.5,
                        "rain": 0.0
                    }
                ],
                "window_len": 10,
                "stride": 1,
                "threshold": 2.5
            }
        }


class AnomalyResult(BaseModel):
    time_start: str = Field(..., description="Window start time")
    time_end: str = Field(..., description="Window end time")
    station_id: str = Field(..., description="Station ID where anomaly occurred")
    variable: str = Field(..., description="Anomalous variable")
    anomaly_timestamp: str = Field(..., description="Exact time of anomaly")
    anomaly_value: float = Field(..., description="The anomalous value")
    z_score: float = Field(..., description="Z-score of the anomalous value")


class DetectionResponse(BaseModel):
    status: str = Field(..., description="Detection status: 'anomalies_found' or 'no_anomalies'")
    message: str = Field(..., description="Human-readable message")
    detection_time: str = Field(..., description="Time when detection was performed")
    total_observations: int = Field(..., description="Total number of observations processed")
    total_anomalies: int = Field(..., description="Total number of anomalies detected")
    parameters: dict = Field(..., description="Detection parameters used")
    anomalies: List[AnomalyResult] = Field(..., description="List of detected anomalies (empty if none found)")


# ============================================================================
# Anomaly Detection Logic
# ============================================================================

def detect_temporal_anomalies(observations: List[Observation], threshold: float = 2.5) -> List[AnomalyResult]:
    """
    Detect temporal anomalies using Z-score method.
    Analyzes each station's time series independently.
    """
    anomalies = []
    
    # Group observations by station
    station_data = defaultdict(list)
    for obs in observations:
        station_data[obs.station_id].append(obs)
    
    # Variables to check
    variables = ['temp_out', 'out_hum', 'wind_speed', 'bar', 'rain']
    
    for station_id, obs_list in station_data.items():
        # Sort by timestamp
        obs_list.sort(key=lambda x: x.timestamp)
        
        if len(obs_list) < 3:  # Need at least 3 points for meaningful statistics
            continue
        
        # Get time window
        timestamps = [obs.timestamp for obs in obs_list]
        time_start = datetime.fromtimestamp(min(timestamps)).strftime("%Y-%m-%d %H:%M:%S")
        time_end = datetime.fromtimestamp(max(timestamps)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Check each variable
        for var in variables:
            values = np.array([getattr(obs, var) for obs in obs_list])
            
            # Skip if all values are the same or too few non-zero values
            if np.std(values) < 1e-6:
                continue
            
            # Calculate Z-scores
            mean = np.mean(values)
            std = np.std(values)
            
            if std > 0:
                z_scores = (values - mean) / std
                
                # Find anomalies
                for i, (obs, z_score) in enumerate(zip(obs_list, z_scores)):
                    if abs(z_score) > threshold:
                        anomalies.append(AnomalyResult(
                            time_start=time_start,
                            time_end=time_end,
                            station_id=station_id,
                            variable=var,
                            anomaly_timestamp=datetime.fromtimestamp(obs.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                            anomaly_value=round(float(getattr(obs, var)), 2),
                            z_score=round(float(z_score), 2)
                        ))
    
    return anomalies


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API information and status"""
    return {
        "name": "Real-Time Data Anomaly Detection API",
        "version": "1.0.0",
        "status": "operational",
        "description": "Weather Time Series Anomaly Detection Service",
        "project": "DataGems EOSC",
        "documentation": "https://datagems-eosc.github.io/real_time_data_profiler/",
        "endpoints": {
            "POST /detect": "Detect anomalies in observation data",
            "GET /test-data": "Get sample test data"
        }
    }




@app.get("/test-data")
async def get_test_data():
    """
    Get sample test data for API testing.
    Returns observations for 10 stations with 60 time points each.
    """
    try:
        with open('api_test_data.json', 'r') as f:
            test_data = json.load(f)
        
        return {
            "message": "Sample test data for 10 stations, 60 time points each",
            "total_observations": len(test_data),
            "stations": list(set(obs['station_id'] for obs in test_data)),
            "time_range": {
                "start": test_data[0]['datetime'] if test_data else None,
                "end": test_data[-1]['datetime'] if test_data else None
            },
            "observations": test_data
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Test data file not found")


@app.post("/detect", response_model=DetectionResponse)
async def detect_anomalies(request: DetectionRequest):
    """
    Detect anomalies in weather time series data.
    
    **Parameters:**
    - **observations**: List of weather observations
    - **window_len** (W): Sliding window length (default: 60)
    - **stride** (S): Sliding stride (default: 18)
    - **threshold**: Z-score threshold for anomaly detection (default: 2.5)
    
    **Returns:**
    - Detection results with list of anomalies found
    
    **Example:**
    ```
    POST /detect
    {
        "observations": [...],
        "window_len": 60,
        "stride": 18,
        "threshold": 2.5
    }
    ```
    """
    if not request.observations:
        raise HTTPException(status_code=400, detail="No observations provided")
    
    if len(request.observations) < 3:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient data: {len(request.observations)} observations provided. Minimum 3 required for statistical analysis."
        )
    
    # Perform anomaly detection
    try:
        anomalies = detect_temporal_anomalies(
            request.observations,
            threshold=request.threshold
        )
        
        # Prepare response
        if len(anomalies) > 0:
            status = "anomalies_found"
            message = f"✓ Detection completed. Found {len(anomalies)} anomalie(s) in {len(request.observations)} observations."
        else:
            status = "no_anomalies"
            message = f"✓ Detection completed. No anomalies detected in {len(request.observations)} observations. All values are within normal range."
        
        response = DetectionResponse(
            status=status,
            message=message,
            detection_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_observations=len(request.observations),
            total_anomalies=len(anomalies),
            parameters={
                "window_len": request.window_len,
                "stride": request.stride,
                "threshold": request.threshold,
                "variables": ["temp_out", "out_hum", "wind_speed", "bar", "rain"]
            },
            anomalies=anomalies
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("Real-Time Data Anomaly Detection API Server")
    print("DataGems EOSC Project")
    print("=" * 70)
    print("\n🚀 Starting server...")
    print("📖 API Documentation: http://0.0.0.0:8000/docs")
    print("🌐 API Base URL: http://0.0.0.0:8000")
    print("   Access from outside: http://YOUR_SERVER_IP:8000")
    print("\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

