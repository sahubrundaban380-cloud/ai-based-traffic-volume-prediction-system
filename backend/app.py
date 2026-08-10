from flask import Flask, request, jsonify
from flask_cors import CORS

import joblib
import pandas as pd

from datetime import datetime


# =========================================================
# APPLICATION
# =========================================================

app = Flask(
    __name__
)

CORS(app)


# =========================================================
# CONFIGURATION
# =========================================================

MODEL_FILE = "model.pkl"


# =========================================================
# LOAD MODEL
# =========================================================

try:

    model = joblib.load(
        MODEL_FILE
    )

    MODEL_LOADED = True

    print(
        "AI model loaded successfully."
    )

except Exception as error:

    model = None

    MODEL_LOADED = False

    print(
        "Model loading failed:"
    )

    print(error)


# =========================================================
# MAPPINGS
# =========================================================

WEATHER_MAP = {

    "Clear": 0,

    "Cloudy": 1,

    "Rain": 2,

    "Fog": 3
}


HOLIDAY_MAP = {

    "No": 0,

    "Yes": 1
}


ROAD_MAP = {

    "Good": 0,

    "Normal": 1,

    "Poor": 2
}


LOCATION_MAP = {

    "Main Road": 0,

    "Highway": 1,

    "City Center": 2,

    "Market Area": 3,

    "School Zone": 4
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_traffic_status(
    traffic
):

    if traffic < 700:

        return "Low Traffic"

    elif traffic < 1400:

        return "Moderate Traffic"

    elif traffic < 2000:

        return "High Traffic"

    else:

        return "Very High Traffic"


# ---------------------------------------------------------

def validate_number(
    value,
    minimum,
    maximum
):

    try:

        number = float(
            value
        )

    except:

        return None


    if number < minimum:

        return None


    if number > maximum:

        return None


    return number


# =========================================================
# HOME
# =========================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({

        "success": True,

        "application":
            "TrafficAI",

        "message":
            "AI-Based Real-Time Traffic Volume Prediction API",

        "status":
            "online",

        "model_loaded":
            MODEL_LOADED

    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success": True,

        "status":
            "online",

        "model_loaded":
            MODEL_LOADED,

        "time":
            datetime.now().isoformat()

    })


# =========================================================
# PREDICTION API
# =========================================================

@app.route(
    "/api/predict",
    methods=["POST"]
)
def predict():

    try:

        # -------------------------------------------------
        # CHECK MODEL
        # -------------------------------------------------

        if not MODEL_LOADED:

            return jsonify({

                "success": False,

                "message":
                    "AI model is not loaded. Run train_model.py first."

            }), 500


        # -------------------------------------------------
        # GET JSON
        # -------------------------------------------------

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "Request body is empty."

            }), 400


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        required_fields = [

            "date",

            "time",

            "location",

            "weather",

            "temperature",

            "holiday",

            "previousTraffic",

            "roadCondition"

        ]


        missing_fields = [

            field

            for field in required_fields

            if field not in data
        ]


        if missing_fields:

            return jsonify({

                "success": False,

                "message":
                    "Missing required fields.",

                "missing":
                    missing_fields

            }), 400


        # -------------------------------------------------
        # READ VALUES
        # -------------------------------------------------

        date = str(
            data["date"]
        )

        time = str(
            data["time"]
        )

        location = str(
            data["location"]
        )

        weather = str(
            data["weather"]
        )

        holiday = str(
            data["holiday"]
        )

        road_condition = str(
            data["roadCondition"]
        )


        # -------------------------------------------------
        # VALIDATE DATE
        # -------------------------------------------------

        try:

            datetime.strptime(
                date,
                "%Y-%m-%d"
            )

        except ValueError:

            return jsonify({

                "success": False,

                "message":
                    "Invalid date format."

            }), 400


        # -------------------------------------------------
        # VALIDATE TIME
        # -------------------------------------------------

        try:

            datetime.strptime(
                time,
                "%H:%M"
            )

        except ValueError:

            return jsonify({

                "success": False,

                "message":
                    "Invalid time format."

            }), 400


        # -------------------------------------------------
        # GET HOUR
        # -------------------------------------------------

        hour = int(
            time.split(":")[0]
        )


        # -------------------------------------------------
        # VALIDATE CATEGORIES
        # -------------------------------------------------

        if location not in LOCATION_MAP:

            return jsonify({

                "success": False,

                "message":
                    "Invalid location."

            }), 400


        if weather not in WEATHER_MAP:

            return jsonify({

                "success": False,

                "message":
                    "Invalid weather."

            }), 400


        if holiday not in HOLIDAY_MAP:

            return jsonify({

                "success": False,

                "message":
                    "Invalid holiday."

            }), 400


        if road_condition not in ROAD_MAP:

            return jsonify({

                "success": False,

                "message":
                    "Invalid road condition."

            }), 400


        # -------------------------------------------------
        # VALIDATE TEMPERATURE
        # -------------------------------------------------

        temperature = validate_number(

            data["temperature"],

            -50,

            60

        )


        if temperature is None:

            return jsonify({

                "success": False,

                "message":
                    "Temperature must be between -50 and 60 °C."

            }), 400


        # -------------------------------------------------
        # VALIDATE PREVIOUS TRAFFIC
        # -------------------------------------------------

        previous_traffic = validate_number(

            data["previousTraffic"],

            0,

            100000

        )


        if previous_traffic is None:

            return jsonify({

                "success": False,

                "message":
                    "Invalid previous traffic volume."

            }), 400


        # -------------------------------------------------
        # CREATE INPUT DATA
        # -------------------------------------------------

        input_data = pd.DataFrame({

            "hour": [

                hour

            ],

            "temperature": [

                temperature

            ],

            "weather": [

                WEATHER_MAP[
                    weather
                ]

            ],

            "holiday": [

                HOLIDAY_MAP[
                    holiday
                ]

            ],

            "previous_traffic": [

                previous_traffic

            ],

            "road_condition": [

                ROAD_MAP[
                    road_condition
                ]

            ],

            "location": [

                LOCATION_MAP[
                    location
                ]

            ]

        })


        # -------------------------------------------------
        # MODEL PREDICTION
        # -------------------------------------------------

        prediction = model.predict(
            input_data
        )


        traffic_volume = max(

            50,

            round(
                float(
                    prediction[0]
                )
            )

        )


        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        status = get_traffic_status(
            traffic_volume
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "prediction":
                traffic_volume,

            "traffic_volume":
                traffic_volume,

            "status":
                status,

            "unit":
                "Vehicles / Hour",

            "model":
                "Random Forest",

            "input": {

                "date":
                    date,

                "time":
                    time,

                "location":
                    location,

                "weather":
                    weather,

                "temperature":
                    temperature,

                "holiday":
                    holiday,

                "previousTraffic":
                    previous_traffic,

                "roadCondition":
                    road_condition

            },

            "timestamp":
                datetime.now().isoformat()

        })


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as error:

        print(
            "\nPrediction Error:"
        )

        print(error)


        return jsonify({

            "success": False,

            "message":
                "An internal server error occurred.",

            "error":
                str(error)

        }), 500


# =========================================================
# 404 HANDLER
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "message":
            "API endpoint not found."

    }), 404


# =========================================================
# 405 HANDLER
# =========================================================

@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({

        "success": False,

        "message":
            "HTTP method not allowed."

    }), 405


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("\n")
    print("==============================================")
    print("        TRAFFIC AI PREDICTION SYSTEM")
    print("==============================================")

    print(
        "API URL: http://127.0.0.1:5000"
    )

    print(
        "Health:  http://127.0.0.1:5000/api/health"
    )

    print(
        "Model:   " +
        (
            "Loaded"
            if MODEL_LOADED
            else "Not Loaded"
        )
    )

    print("==============================================")
    print("\n")


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )