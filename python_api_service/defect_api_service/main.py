import os
import io # For handling byte streams, useful for image processing
from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
from PIL import Image # For opening and manipulating images

# --- Configuration ---
MODEL_PATH = "best.pt"

# --- Initialize FastAPI App ---
app = FastAPI(title="Defect Detection API")

# --- Global variable to hold the loaded model ---
# We use a global variable here so it can be accessed by the startup event and endpoints.
model = None

# --- Load YOLO Model on Application Startup ---
@app.on_event("startup")
def load_model_on_startup():
    """
    This function is executed when the FastAPI application starts.
    It loads the YOLO model into the global 'model' variable.
    """
    global model # Declare that we are using the global 'model' variable
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model file not found at '{MODEL_PATH}'. The API will start, but /inspect will fail.")
        return

    try:
        model = YOLO(MODEL_PATH)
        print(f"Successfully loaded YOLO model from: {MODEL_PATH}")
    except Exception as e:
        print(f"ERROR: Failed to load YOLO model from '{MODEL_PATH}'.")
        print(f"Error details: {e}")

# --- Root Endpoint (Optional - for a basic API check) ---
@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    if model:
        return {"message": "Welcome to the Defect Detection API! Model loaded."}
    else:
        return {"message": "Welcome to the Defect Detection API! WARNING: Model failed to load."}
    

# --- Helper Function to Process YOLO Results ---
def process_detection_results(results, yolo_model): # Added yolo_model to access class names
    """
    Processes the detection results from YOLO into a structured list of detections.
    Each detection includes class name, confidence, and coordinates.
    """
    detections = []
    if results and results[0].boxes is not None: # results is a list, access the first element
        for box in results[0].boxes:
            class_id = int(box.cls)
            # Ensure the model object has 'names' attribute (standard for ultralytics YOLO models)
            class_name = yolo_model.names[class_id] if hasattr(yolo_model, 'names') else f"class_{class_id}"
            confidence = float(box.conf)
            # Get coordinates in [xmin, ymin, xmax, ymax] format
            coordinates = box.xyxy[0].tolist()

            detections.append({
                "class_name": class_name,
                "confidence": round(confidence, 4), # Round for cleaner output
                "coordinates": [round(c, 2) for c in coordinates] # Round coordinates
            })
    return detections


# --- API Endpoint for Defect Inspection ---
@app.post("/inspect/")
async def inspect_image_for_defects(file: UploadFile = File(...)):
    """
    Accepts an image file, performs defect detection using the loaded YOLO model,
    and returns the detection results.
    """
    global model # Access the globally loaded model

    if model is None:
        # This check is important if model loading failed on startup
        return {"error": "Model not loaded. Cannot perform inspection. Please check server logs."}

    try:
        # 1. Read the image file uploaded by the client
        image_contents = await file.read()

        # 2. Convert the image bytes to a PIL Image object
        pil_image = Image.open(io.BytesIO(image_contents))

        # 3. Perform inference using the loaded YOLO model
        detection_results = model(pil_image)

        # 4. Process the raw results into a more user-friendly format
        processed_detections = process_detection_results(detection_results, model)

        # 5. Return the results
        if not processed_detections:
            return {
                "filename": file.filename,
                "message": "No defects detected.",
                "detections": []
            }
        else:
            return {
                "filename": file.filename,
                "detections": processed_detections
            }

    except Exception as e:
        return {"error": f"An error occurred while processing the image: {str(e)}"}