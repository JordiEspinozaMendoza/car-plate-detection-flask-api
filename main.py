from flask import Flask, jsonify, request
from utils.predictions import getPredictionFromRoboflow
from utils.images import cutImage, labelImage
from dotenv import load_dotenv
from flask_cors import CORS
from PIL import Image
import os
import io
import sys

load_dotenv()

origins = os.environ.get("ORIGINS", "*").split(",")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./uploads"
cors = CORS(app, resources={r"/*": {"origins": origins}})


@app.route("/notify/v1/health")
def health_check():
    return jsonify({"status": "UP"})


@app.route("/api/process-image/", methods=["POST"])
def process_image():
    try:
        image = request.files["file"].read()
        detections = getPredictionFromRoboflow(image)

        file = Image.open(io.BytesIO(image))

        results = labelImage(file, detections)
        car_plates = []

        for res in detections:
            if res["name"] == "car-plate":
                result = cutImage(file, res)
                text = ""

                car_plates.append(
                    {"image": result["image"].decode("utf-8"), "text": text}
                )

        return jsonify(
            {
                "results": results.decode("utf-8"),
                "car_plates": car_plates,
                "error": "",
                "status": "success",
            }
        )
    except Exception as e:
        error = str(e)

        print(e, sys.exc_info()[-1].tb_lineno)

        return jsonify(
            {"results": [], "car_plates": [], "error": error, "status": "error"}
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
