
// Auto hide after 10 seconds
setTimeout(function () {
    document.querySelectorAll(".auto-hide").forEach(function (el) {
        fadeOut(el);
    });
}, 10000);

// Manual close
function closeAlert(btn) {
    const el = btn.closest(".auto-hide");
    fadeOut(el);
}

// Fade out function
function fadeOut(el) {
    el.style.transition = "opacity 0.5s";
    el.style.opacity = "0";

    setTimeout(() => {
        el.remove();
    }, 500);
}
