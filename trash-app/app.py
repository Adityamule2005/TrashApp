from flask import Flask, request, render_template, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import json
import os
import google.generativeai as genai

# ==============================
# PATH SETUP (Jenkins Safe)
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(STATIC_DIR, exist_ok=True)

# ==============================
# FLASK APP INIT
# ==============================
app = Flask(__name__, template_folder=TEMPLATE_DIR)

# ==============================
# LOAD ML MODEL
# ==============================
MODEL_PATH = os.path.join(BASE_DIR, "trash_classifier_v6.h5")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

model = load_model(MODEL_PATH)
print("✅ ML model loaded successfully")

# ==============================
# LOAD CLASS INDICES
# ==============================
CLASS_INDEX_PATH = os.path.join(BASE_DIR, "class_indices.json")

with open(CLASS_INDEX_PATH, "r") as f:
    class_indices = json.load(f)

idx_to_class = {v: k for k, v in class_indices.items()}

# ==============================
# IMAGE PREDICTION FUNCTION
# ==============================
def predict_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array)
    pred_class = np.argmax(preds, axis=1)[0]
    confidence = float(np.max(preds))

    return idx_to_class[pred_class], confidence

# ==============================
# GEMINI API CONFIG
# ==============================
gemini_api_key = os.getenv("GOOGLE_API_KEY")

if not gemini_api_key:
    print("❌ GOOGLE_API_KEY not set. Gemini API disabled.")
    gemini_model = None
else:
    try:
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel("gemini-pro")
        print("✅ Gemini API configured successfully")
    except Exception as e:
        print(f"❌ Gemini init failed: {e}")
        gemini_model = None

# ==============================
# ROUTES
# ==============================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        file_path = os.path.join(STATIC_DIR, file.filename)
        file.save(file_path)

        label, confidence = predict_image(file_path)

        return render_template(
            "index.html",
            uploaded_image=f"static/{file.filename}",
            prediction=label,
            confidence=round(confidence * 100, 2),
        )

    return render_template("index.html")


@app.route("/get_disposal_suggestion", methods=["POST"])
def get_disposal_suggestion():
    if gemini_model is None:
        return jsonify({"error": "AI service not configured"}), 503

    try:
        data = request.get_json()
        trash_type = data.get("trash_type")

        if not trash_type:
            return jsonify({"error": "Trash type not provided"}), 400

        prompt = f"""
        Provide eco-friendly disposal and recycling tips for '{trash_type}'.

        Format:
        1. Primary Disposal Method
        2. Recycling or Reuse Ideas
        3. Important Note
        """

        response = gemini_model.generate_content(prompt)

        return jsonify({"suggestion": response.text})

    except Exception as e:
        print(f"Gemini error: {e}")
        return jsonify({"error": "Failed to get AI suggestion"}), 500

# ==============================
# APP START
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
