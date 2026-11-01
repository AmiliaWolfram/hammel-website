document.addEventListener("DOMContentLoaded", () => { const elements = document.querySelectorAll(".about-milestone,.about-gallery img,.about-members-grid article"); if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches)
    return; elements.forEach(e => e.classList.add("about-animate")); const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) {
    entry.target.classList.add("about-visible");
    observer.unobserve(entry.target);
} }), { threshold: .09 }); elements.forEach(e => observer.observe(e)); });
