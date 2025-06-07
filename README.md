# SRCIM Lab 2: AI Defect Detection in a Manufacturing CPS

## 1. Project Overview

This repository contains the full implementation for the SRCIM Lab Assignment 2 (2024/2025). The project integrates a YOLO-based deep learning model for defect detection into a Java/JADE-based Cyber-Physical System (CPS) that controls a manufacturing cell simulated in CoppeliaSim.

The project consists of three main components that must run concurrently:
1.  **Python FastAPI Service:** An API that loads the trained YOLO model and exposes an `/inspect` endpoint to check images for defects.
2.  **Java Agent-Based CPS:** The JADE multi-agent system from Lab 1, which orchestrates the manufacturing process. It has been modified to call the Python API for quality control.
3.  **CoppeliaSim Simulation:** The virtual environment containing the robots, conveyors, and sensors.

---

## 2. Directory Structure

-   `/java_cps_project/`: Contains the Java/JADE-based CPS (a Maven project).
    -   `/images/`: Target directory for CoppeliaSim to save inspection images.
    -   `/src/main/java/Libraries/SimResourceLibrary.java`: Modified to call the Python API.
-   `/python_api_service/`: Contains the Python FastAPI service.
    -   `/models/best.pt`: The trained YOLO model weights.
    -   `main.py`: The main script for the FastAPI application.
    -   `requirements.txt`: A list of all required Python packages.
-   `/coppelia_sim_scene/`: Contains the CoppeliaSim scene file (`.ttt`).

---

## 3. How to Run the System

### Step A: Start the Python API Service

```bash
# Navigate to the API directory
cd python_api_service

# Create and activate a virtual environment
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Run the API server
uvicorn main:app --reload
```
The API will be running at `http://127.0.0.1:8000`.

### Step B: Start the Java CPS

1.  Open the `java_cps_project` folder as a Maven project in a Java IDE (e.g., IntelliJ, Eclipse).
2.  Run the JADE Main Container configuration. The startup arguments are:
    `-gui Operator:Resource.ResourceAgent("Operator","Operator","SimResourceLibrary");GlueStation1:Resource.ResourceAgent("GlueStation1","GlueStation1","SimResourceLibrary");GlueStation2:Resource.ResourceAgent("GlueStation2","GlueStation2","SimResourceLibrary");QualityControlStation1:Resource.ResourceAgent("QualityControlStation1","QualityControlStation1","SimResourceLibrary");AGV:Transport.TransportAgent("AGV","AGV","SimTransportLibrary");ProductC:Product.ProductAgent("ProductC","C")`

### Step C: Start the CoppeliaSim Simulation

1.  Open the CoppeliaSim application.
2.  Open the scene file located in the `/coppelia_sim_scene/` directory.
3.  **CRITICAL:** Before running, you must edit the **`ControlServer` script** inside CoppeliaSim. Set its `iPath` variable to the correct **absolute path** of the `/java_cps_project/images/` folder on your machine.
4.  Click the "Start simulation" button.

---

## 4. Current Project Status & Context

-   The AI model (`best.pt`) has been trained and is served by the FastAPI API.
-   The Java `SimResourceLibrary.java` has been modified to call the API.
-   The CoppeliaSim environment and Lua scripts (`youBot`, `ControlServer`, etc.) have been extensively debugged to fix Python environment issues, deprecated API calls, and object pathing errors.
-   **Current Blocker:** When the full system is run, there are no crashing errors, but the `youBot` AGV and conveyors in CoppeliaSim **do not move**. The Java agents send commands, but the simulation remains static. The root cause is a silent failure in the command logic within the CoppeliaSim scripts. The immediate next step is to debug the `youBot` and conveyor scripts to find out why they are not acting on the signals received from the Java agents.