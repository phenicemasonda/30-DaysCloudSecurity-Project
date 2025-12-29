// static/js/app.js

document.addEventListener("DOMContentLoaded", () => {
    console.log("Verdant Secure ID Gateway loaded");

    const form = document.getElementById("loginForm");
    if (!form) return;

    form.addEventListener("submit", () => {
        const btnText = document.getElementById("btnText");
        const spinner = document.getElementById("btnSpinner");

        btnText.textContent = "Redirecting…";
        spinner.classList.remove("hidden");
    });
});
