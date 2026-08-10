/* =========================================================
   TRAFFIC AI - PREDICTION JAVASCRIPT
   Handles prediction form and result
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const predictionForm =
        document.getElementById("predictionForm");

    const predictionResult =
        document.getElementById("predictionResult");

    const resultValue =
        document.getElementById("resultValue");

    const trafficStatus =
        document.getElementById("trafficStatus");


    /* ================= FORM SUBMIT ================= */

    if (predictionForm) {

        predictionForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();

                /* Get values */

                const date =
                    document.getElementById("date").value;

                const time =
                    document.getElementById("time").value;

                const location =
                    document.getElementById("location").value;

                const weather =
                    document.getElementById("weather").value;

                const temperature =
                    Number(
                        document.getElementById("temperature").value
                    );

                const holiday =
                    document.getElementById("holiday").value;

                const previousTraffic =
                    Number(
                        document.getElementById(
                            "previousTraffic"
                        ).value
                    );

                const roadCondition =
                    document.getElementById(
                        "roadCondition"
                    ).value;


                /* ================= VALIDATION ================= */

                if (
                    !date ||
                    !time ||
                    !location ||
                    !weather ||
                    !holiday ||
                    !roadCondition
                ) {

                    showMessage(
                        "Please fill all required fields.",
                        "danger"
                    );

                    return;
                }


                if (temperature < -50 || temperature > 60) {

                    showMessage(
                        "Please enter a valid temperature.",
                        "danger"
                    );

                    return;
                }


                if (previousTraffic < 0) {

                    showMessage(
                        "Traffic volume cannot be negative.",
                        "danger"
                    );

                    return;
                }


                /* ================= BUTTON LOADING ================= */

                const button =
                    predictionForm.querySelector(
                        "button[type='submit']"
                    );

                const originalText =
                    button.innerHTML;

                button.disabled = true;

                button.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2"></span>' +
                    'Analyzing Traffic...';


                /* ================= AI DEMO PREDICTION ================= */

                setTimeout(function () {

                    const prediction =
                        calculateDemoPrediction(
                            time,
                            weather,
                            temperature,
                            holiday,
                            previousTraffic,
                            roadCondition,
                            location
                        );


                    /* Show result */

                    displayPrediction(prediction);


                    /* Restore button */

                    button.disabled = false;

                    button.innerHTML = originalText;


                    /* Scroll to result */

                    predictionResult.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });

                }, 1200);

            }
        );

    }


    /* =====================================================
       DEMO PREDICTION FUNCTION

       IMPORTANT:
       Replace this function later with your backend
       machine-learning API.
       ===================================================== */

    function calculateDemoPrediction(
        time,
        weather,
        temperature,
        holiday,
        previousTraffic,
        roadCondition,
        location
    ) {

        let traffic = previousTraffic;


        /* Time factor */

        const hour =
            parseInt(time.split(":")[0]);

        if (hour >= 7 && hour <= 10) {

            traffic *= 1.25;

        } else if (hour >= 17 && hour <= 21) {

            traffic *= 1.30;

        } else if (hour >= 11 && hour <= 16) {

            traffic *= 1.05;

        } else {

            traffic *= 0.75;
        }


        /* Weather factor */

        if (weather === "Rain") {

            traffic *= 1.12;

        } else if (weather === "Fog") {

            traffic *= 1.08;

        } else if (weather === "Cloudy") {

            traffic *= 1.03;
        }


        /* Temperature factor */

        if (temperature > 35) {

            traffic *= 1.04;

        } else if (temperature < 15) {

            traffic *= 0.96;
        }


        /* Holiday */

        if (holiday === "Yes") {

            traffic *= 0.70;
        }


        /* Road condition */

        if (roadCondition === "Poor") {

            traffic *= 1.15;

        } else if (roadCondition === "Good") {

            traffic *= 0.95;
        }


        /* Location factor */

        if (location === "Highway") {

            traffic *= 1.10;

        } else if (location === "City Center") {

            traffic *= 1.15;

        } else if (location === "Market Area") {

            traffic *= 1.12;

        } else if (location === "School Zone") {

            traffic *= 1.08;
        }


        /* Small random variation */

        const variation =
            0.95 + Math.random() * 0.10;

        traffic *= variation;


        /* Round */

        traffic =
            Math.round(traffic);


        /* Prevent unrealistic zero */

        if (traffic < 50) {
            traffic = 50;
        }


        return traffic;
    }


    /* ================= DISPLAY RESULT ================= */

    function displayPrediction(value) {

        resultValue.textContent =
            formatNumber(value) +
            " Vehicles / Hour";


        let status = "";
        let statusClass = "";


        if (value < 700) {

            status = "Low Traffic";
            statusClass = "low";

        } else if (value < 1400) {

            status = "Moderate Traffic";
            statusClass = "moderate";

        } else if (value < 2000) {

            status = "High Traffic";
            statusClass = "high";

        } else {

            status = "Very High Traffic";
            statusClass = "very-high";
        }


        trafficStatus.textContent = status;


        trafficStatus.className = "";

        trafficStatus.classList.add(
            "traffic-result-status",
            statusClass
        );


        predictionResult.classList.remove("d-none");


        /* Save prediction */

        localStorage.setItem(
            "lastTrafficPrediction",
            value
        );

        localStorage.setItem(
            "lastTrafficStatus",
            status
        );

    }


    /* ================= NUMBER FORMAT ================= */

    function formatNumber(number) {

        return number.toLocaleString("en-IN");

    }


    /* ================= MESSAGE ================= */

    function showMessage(message, type) {

        const oldAlert =
            document.querySelector(".custom-alert");

        if (oldAlert) {
            oldAlert.remove();
        }


        const alert =
            document.createElement("div");

        alert.className =
            `alert alert-${type} custom-alert mt-3`;

        alert.innerHTML =
            `<i class="bi bi-exclamation-circle me-2"></i>
             ${message}`;


        predictionForm.prepend(alert);


        setTimeout(function () {

            alert.remove();

        }, 3500);

    }

});
fetch("http://127.0.0.1:5000/api/predict", {
    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify({
        date: date,
        time: time,
        location: location,
        weather: weather,
        temperature: Number(temperature),
        holiday: holiday,
        previousTraffic: Number(previousTraffic),
        roadCondition: roadCondition
    })
});