/**
 * FaceAttend AI – Global Script
 * Shared utilities used across all pages
 */

// ── Animate stat numbers on home page ──
function animateCounter(el, target) {
    let current = 0;
    const step = Math.ceil(target / 30);
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            el.textContent = target;
            clearInterval(timer);
        } else {
            el.textContent = current;
        }
    }, 40);
}

// ── Run counters if stat elements are present ──
document.addEventListener("DOMContentLoaded", () => {
    const numEls = document.querySelectorAll(".stat-number");
    numEls.forEach(el => {
        const val = parseInt(el.textContent);
        if (!isNaN(val) && val > 0) animateCounter(el, val);
    });

    // Highlight current nav link based on path
    const path = window.location.pathname;
    document.querySelectorAll(".nav-links a").forEach(a => {
        a.classList.remove("active");
        if (a.getAttribute("href") === path) a.classList.add("active");
    });
});
