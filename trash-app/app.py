import os
import numpy as np
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from PIL import Image
import google.generativeai as genai

# ---------------- CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "trash_classifier_v6.h5")

GENAI_API_KEY = os.getenv("GENAI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=GENAI_API_KEY)

# ---------------- APP ----------------
app = Flask(__name__)

# ---------------- LOAD MODEL ----------------
try:
    model = load_model(MODEL_PATH)
    print("ML model loaded successfully")
except Exception as e:
    print("Error loading model:", e)
    model = None

CLASS_NAMES = [
    "Cardboard",
    "Glass",
    "Metal",
    "Paper",
    "Plastic",
    "Trash"
]

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Trash Classification API is running"})

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    try:
        image = Image.open(file).convert("RGB")
        image = image.resize((224, 224))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        prediction = model.predict(image_array)
        class_index = np.argmax(prediction)
        class_name = CLASS_NAMES[class_index]

        return jsonify({
            "prediction": class_name,
            "confidence": float(np.max(prediction))
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

