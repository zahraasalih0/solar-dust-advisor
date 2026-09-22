(function () {
    function initDustParticles() {
        const canvas = document.getElementById("dust-particles-canvas");
        if (!canvas || canvas.dataset.ready === "true") return;

        const header = canvas.closest(".topbar");
        const context = canvas.getContext("2d");
        const particles = [];
        let width = 0;
        let height = 0;

        function resize() {
            const bounds = header.getBoundingClientRect();
            const scale = window.devicePixelRatio || 1;
            width = bounds.width;
            height = bounds.height;
            canvas.width = width * scale;
            canvas.height = height * scale;
            canvas.style.width = width + "px";
            canvas.style.height = height + "px";
            context.setTransform(scale, 0, 0, scale, 0, 0);
        }

        function seedParticles() {
            particles.length = 0;
            const count = Math.max(18, Math.round(width / 55));
            for (let index = 0; index < count; index += 1) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    radius: 1 + Math.random() * 2.5,
                    speed: 0.08 + Math.random() * 0.16,
                    drift: (Math.random() - 0.5) * 0.12,
                    opacity: 0.15 + Math.random() * 0.15,
                });
            }
        }

        function animate() {
            context.clearRect(0, 0, width, height);
            particles.forEach(function (particle) {
                particle.y -= particle.speed;
                particle.x += particle.drift;
                if (particle.y < -5) particle.y = height + 5;
                if (particle.x < -5) particle.x = width + 5;
                if (particle.x > width + 5) particle.x = -5;
                context.beginPath();
                context.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                context.fillStyle = "rgba(224, 211, 186, " + particle.opacity + ")";
                context.fill();
            });
            window.requestAnimationFrame(animate);
        }

        resize();
        seedParticles();
        window.addEventListener("resize", function () {
            resize();
            seedParticles();
        });
        canvas.dataset.ready = "true";
        animate();
    }

    document.addEventListener("DOMContentLoaded", initDustParticles);
    new MutationObserver(initDustParticles).observe(document.body, { childList: true, subtree: true });
}());
