from flask import Flask, jsonify, render_template_string, request
from gpiozero import AngularServo

app = Flask(__name__)

servo = AngularServo(
    18,
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.001,
    max_pulse_width=0.002
)

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport"
          content="width=device-width, initial-scale=1">
    <title>Servo Controller</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 40px 20px;
            background: #151515;
            color: white;
        }

        h1 {
            font-size: 28px;
        }

        #angle {
            font-size: 42px;
            margin: 30px;
        }

        input[type="range"] {
            width: min(90%, 500px);
        }

        button {
            margin-top: 30px;
            padding: 14px 25px;
            font-size: 18px;
        }
    </style>
</head>

<body>
    <h1>Servo Controller</h1>

    <div id="angle">0°</div>

    <input
        id="slider"
        type="range"
        min="-45"
        max="45"
        value="0"
        step="1"
    >

    <br>

    <button onclick="centreServo()">Centre</button>

    <script>
        const slider = document.getElementById("slider");
        const angleDisplay = document.getElementById("angle");

        let timer;

        function sendAngle(angle) {
            angleDisplay.textContent = angle + "°";

            clearTimeout(timer);

            timer = setTimeout(() => {
                fetch("/angle", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        angle: Number(angle)
                    })
                });
            }, 40);
        }

        slider.addEventListener("input", () => {
            sendAngle(slider.value);
        });

        function centreServo() {
            slider.value = 0;
            sendAngle(0);
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/angle", methods=["POST"])
def set_angle():
    data = request.get_json()
    angle = float(data["angle"])

    if not -45 <= angle <= 45:
        return jsonify(error="Angle outside safe range"), 400

    servo.angle = angle
    return jsonify(angle=angle)


try:
    servo.angle = 0
    app.run(host="0.0.0.0", port=4000, debug=False)

finally:
    servo.detach()
    servo.close()
