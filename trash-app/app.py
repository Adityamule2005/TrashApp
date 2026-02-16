from flask import Flask, request, render_template, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import json
import os
import google.generativeai as genai

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = r"C:\Users\admin\Desktop\Trash-Appv2\trash-app\templates"   # outside backend

# Initialize app

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Load model
MODEL_PATH = "trash_classifier_v6.h5"
model = load_model(MODEL_PATH)

# Load class mapping
with open("class_indices.json") as f:
    class_indices = json.load(f)
idx_to_class = {v: k for k, v in class_indices.items()}


def predict_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array)
    pred_class = np.argmax(preds, axis=1)[0]
    confidence = float(np.max(preds))
    return idx_to_class[pred_class], confidence

# --- NEW: Configure Google Gemini API (Robust Method) ---
# This method provides clear feedback upon starting the app.
gemini_api_key = os.getenv("GOOGLE_API_KEY")

if not gemini_api_key:
    # If the key is not found, print an error and the feature will be disabled.
    print("❌ ERROR: GOOGLE_API_KEY environment variable not set. Gemini API will not function.")
    gemini_model = None # Set model to None so we can handle it later
else:
    # If the key is found, configure the API and print a success message.
    try:
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini API configured successfully.")
    except Exception as e:
        print(f"❌ ERROR: Failed to configure Gemini API: {e}")
        gemini_model = None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"})

        file_path = os.path.join("static", file.filename)
        file.save(file_path)

        label, confidence = predict_image(file_path)
        return render_template(
            "index.html",
            uploaded_image=file_path,
            prediction=label,
            confidence=round(confidence * 100, 2),
        )

    return render_template("index.html")
# --- New: Gemini API Route ---
@app.route("/get_disposal_suggestion", methods=["POST"])
def get_disposal_suggestion():
    """
    API endpoint to get disposal tips from Gemini.
    """
    try:
        data = request.get_json()
        trash_type = data.get("trash_type")

        if not trash_type:
            return jsonify({"error": "Trash type not provided"}), 400

        # Initialize the Gemini Model
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create a detailed prompt
        prompt = f"""
        Provide practical, eco-friendly disposal and recycling tips for: '{trash_type}'.

        Please structure your response as follows:
        1.  **Primary Disposal Method:** The most common and correct way to dispose of it.
        2.  **Recycling/Repurposing Ideas:** Creative ways to reuse or recycle the item.
        3.  **Important Note:** A key piece of advice or a common mistake to avoid.

        Keep the tone helpful and easy to understand for a general audience.
        """
        
        # Get the response from Gemini
        response = gemini_model.generate_content(prompt)
        
        return jsonify({"suggestion": response.text})

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to get suggestions from AI model."}), 500


if __name__ == "__main__":
    app.run(debug=True)
