
from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import cv2
from werkzeug.utils import secure_filename

# Import our Real-ESRGAN restoration function
from restore import restore_image as ai_restore_image

# Project folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "frontend")
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Flask application
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# Home page
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


# Image restoration API
@app.route("/api/restore", methods=["POST"])
def restore_api():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "Please select an image"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only JPG and PNG images allowed"}), 400

    filename = secure_filename(file.filename)
    extension = filename.rsplit(".", 1)[1].lower()

    unique_id = uuid.uuid4().hex

    input_name = unique_id + "." + extension
    output_name = unique_id + "_restored.png"

    input_path = os.path.join(UPLOAD_FOLDER, input_name)
    output_path = os.path.join(OUTPUT_FOLDER, output_name)

    file.save(input_path)

    # Check uploaded image
    image = cv2.imread(input_path)

    if image is None:
        os.remove(input_path)
        return jsonify({"error": "Invalid image file"}), 400

    try:
        # Restore image using Real-ESRGAN
        ai_restore_image(input_path, output_path)

        return jsonify({
            "message": "AI image restoration completed successfully",
            "original": "/files/uploads/" + input_name,
            "restored": "/files/outputs/" + output_name
        })

    except Exception as error:
        print("Restoration error:", error)

        return jsonify({
            "error": "Image restoration failed. Please check the server terminal."
        }), 500


# Display original image
@app.route("/files/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# Display restored image
@app.route("/files/outputs/<filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)
