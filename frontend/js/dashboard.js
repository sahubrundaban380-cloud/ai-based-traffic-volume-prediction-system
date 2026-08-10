/* =========================================================
   TRAFFIC AI - DASHBOARD JAVASCRIPT
   Dashboard + Chart + Real-Time Simulation
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* ================= GET ELEMENTS ================= */

    const trafficElement =
        document.getElementById("currentTraffic");

    const levelElement =
        document.getElementById("trafficLevel");

    const nextHourElement =
        document.getElementById("nextHourTraffic");

    const updatedElement =
        document.getElementById("lastUpdated");

    const chartCanvas =
        document.getElementById("trafficChart");

    const chartPeriod =
        document.getElementById("chartPeriod");


    /* ================= LOAD LAST PREDICTION ================= */

    const savedPrediction =
        localStorage.getItem(
            "lastTrafficPrediction"
        );

    const savedStatus =
        localStorage.getItem(
            "lastTrafficStatus"
        );


    if (savedPrediction) {

        const prediction =
            Number(savedPrediction);

        trafficElement.textContent =
            formatNumber(prediction);

        nextHourElement.textContent =
            formatNumber(
                Math.round(prediction * 1.08)
            );

    }


    if (savedStatus) {

        levelElement.textContent =
            savedStatus;

        setTrafficLevelStyle(
            savedStatus
        );

    }


    /* ================= CHART DATA ================= */

    const todayLabels = [
        "6 AM",
        "8 AM",
        "10 AM",
        "12 PM",
        "2 PM",
        "4 PM",
        "6 PM",
        "8 PM",
        "10 PM"
    ];


    const todayData = [
        520,
        1250,
        980,
        760,
        850,
        1100,
        1680,
        1520,
        900
    ];


    const weekLabels = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
    ];


    const weekData = [
        1180,
        1320,
        1250,
        1410,
        1580,
        1100,
        980
    ];


    const monthLabels = [
        "Week 1",
        "Week 2",
        "Week 3",
        "Week 4"
    ];


    const monthData = [
        1240,
        1380,
        1510,
        1450
    ];


    /* ================= CHART ================= */

    let trafficChart = null;


    function createChart(
        labels,
        data
    ) {

        if (!chartCanvas) {
            return;
        }


        if (trafficChart) {

            trafficChart.destroy();

        }


        const ctx =
            chartCanvas.getContext("2d");


        /* Gradient */

        const gradient =
            ctx.createLinearGradient(
                0,
                0,
                0,
                300
            );

        gradient.addColorStop(
            0,
            "rgba(0, 180, 216, 0.35)"
        );

        gradient.addColorStop(
            1,
            "rgba(0, 180, 216, 0)"
        );


        trafficChart =
            new Chart(
                ctx,
                {

                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [

                            {

                                label:
                                    "Traffic Volume",

                                data: data,

                                borderColor:
                                    "#00b4d8",

                                backgroundColor:
                                    gradient,

                                borderWidth: 3,

                                fill: true,

                                tension: 0.4,

                                pointRadius: 4,

                                pointHoverRadius: 7,

                                pointBackgroundColor:
                                    "#00b4d8",

                                pointBorderColor:
                                    "#ffffff",

                                pointBorderWidth: 2

                            }

                        ]

                    },


                    options: {

                        responsive: true,

                        maintainAspectRatio: false,


                        interaction: {

                            intersect: false,

                            mode: "index"

                        },


                        plugins: {

                            legend: {

                                display: false

                            },


                            tooltip: {

                                backgroundColor:
                                    "#0b192b",

                                titleColor:
                                    "#ffffff",

                                bodyColor:
                                    "#c8d4e3",

                                borderColor:
                                    "rgba(255,255,255,0.1)",

                                borderWidth: 1,

                                padding: 12,


                                callbacks: {

                                    label:
                                        function (context) {

                                            return (
                                                " Traffic: " +
                                                context.parsed.y
                                                    .toLocaleString(
                                                        "en-IN"
                                                    ) +
                                                " vehicles"
                                            );

                                        }

                                }

                            }

                        },


                        scales: {

                            x: {

                                grid: {

                                    color:
                                        "rgba(255,255,255,0.05)"

                                },

                                ticks: {

                                    color:
                                        "#8798ad",

                                    font: {

                                        size: 11

                                    }

                                }

                            },


                            y: {

                                beginAtZero: true,

                                grid: {

                                    color:
                                        "rgba(255,255,255,0.05)"

                                },

                                ticks: {

                                    color:
                                        "#8798ad",

                                    font: {

                                        size: 11

                                    }

                                }

                            }

                        }

                    }

                }
            );

    }


    /* Initial chart */

    createChart(
        todayLabels,
        todayData
    );


    /* ================= CHANGE CHART PERIOD ================= */

    if (chartPeriod) {

        chartPeriod.addEventListener(
            "change",
            function () {

                const selected =
                    this.value;


                if (selected === "today") {

                    createChart(
                        todayLabels,
                        todayData
                    );

                } else if (selected === "week") {

                    createChart(
                        weekLabels,
                        weekData
                    );

                } else {

                    createChart(
                        monthLabels,
                        monthData
                    );

                }

            }
        );

    }


    /* ================= REAL-TIME SIMULATION ================= */

    function updateTraffic() {

        let current =
            parseInt(
                trafficElement.textContent
                    .replace(/,/g, "")
            );


        if (isNaN(current)) {

            current = 1284;

        }


        /* Small traffic change */

        const change =
            Math.floor(
                Math.random() * 61
            ) - 30;


        current += change;


        if (current < 300) {

            current = 300;

        }


        if (current > 3000) {

            current = 3000;

        }


        trafficElement.textContent =
            formatNumber(current);


        /* Calculate traffic level */

        let level;


        if (current < 700) {

            level = "Low";

        } else if (current < 1400) {

            level = "Moderate";

        } else if (current < 2000) {

            level = "High";

        } else {

            level = "Very High";

        }


        levelElement.textContent =
            level;


        setTrafficLevelStyle(
            level
        );


        /* Next hour prediction */

        const next =
            Math.round(
                current * (1.05 + Math.random() * 0.12)
            );


        nextHourElement.textContent =
            formatNumber(next);


        /* Update timestamp */

        if (updatedElement) {

            updatedElement.textContent =
                getCurrentTime();

        }

    }


    /* Update every 5 seconds */

    setInterval(
        updateTraffic,
        5000
    );


    /* ================= TRAFFIC LEVEL STYLE ================= */

    function setTrafficLevelStyle(level) {

        if (!levelElement) {
            return;
        }


        levelElement.classList.remove(
            "text-success",
            "text-warning",
            "text-danger"
        );


        if (
            level.toLowerCase().includes("low")
        ) {

            levelElement.classList.add(
                "text-success"
            );

        } else if (
            level.toLowerCase().includes("moderate")
        ) {

            levelElement.classList.add(
                "text-warning"
            );

        } else {

            levelElement.classList.add(
                "text-danger"
            );

        }

    }


    /* ================= TIME ================= */

    function getCurrentTime() {

        const now =
            new Date();


        return now.toLocaleTimeString(
            "en-IN",
            {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            }
        );

    }


    /* ================= NUMBER FORMAT ================= */

    function formatNumber(number) {

        return Number(number).toLocaleString(
            "en-IN"
        );

    }

});