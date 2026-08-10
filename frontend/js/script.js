/* =========================================================
   TRAFFIC AI - MAIN JAVASCRIPT
   General website functionality
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* ================= CURRENT YEAR ================= */

    const yearElements = document.querySelectorAll(".current-year");

    yearElements.forEach(function (element) {
        element.textContent = new Date().getFullYear();
    });


    /* ================= NAVBAR SCROLL ================= */

    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", function () {

        if (window.scrollY > 50) {

            navbar.style.background = "rgba(5, 13, 24, 0.98)";
            navbar.style.boxShadow = "0 5px 25px rgba(0,0,0,0.2)";

        } else {

            navbar.style.background = "rgba(7, 17, 31, 0.92)";
            navbar.style.boxShadow = "none";
        }

    });


    /* ================= SMOOTH NAVIGATION ================= */

    const internalLinks = document.querySelectorAll(
        'a[href^="#"]'
    );

    internalLinks.forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId = this.getAttribute("href");

            if (targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (target) {

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth"
                });

            }

        });

    });


    /* ================= PAGE FADE IN ================= */

    document.body.style.opacity = "0";

    setTimeout(function () {

        document.body.style.transition = "opacity 0.5s ease";

        document.body.style.opacity = "1";

    }, 100);


    /* ================= ACTIVE NAVIGATION ================= */

    const currentPage =
        window.location.pathname.split("/").pop();

    const navLinks =
        document.querySelectorAll(".navbar .nav-link");

    navLinks.forEach(function (link) {

        const linkPage =
            link.getAttribute("href");

        if (linkPage === currentPage) {

            navLinks.forEach(function (item) {
                item.classList.remove("active");
            });

            link.classList.add("active");
        }

    });

});