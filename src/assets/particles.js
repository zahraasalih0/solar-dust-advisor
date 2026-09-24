(function () {
    function initDustParticles() {
        const canvas = document.getElementById("gauge-dust-canvas");
        if (!canvas || canvas.dataset.ready === "true") return;

        const card = canvas.closest(".gauge-card");
        const context = canvas.getContext("2d");
        const particles = [];
        let width = 0;
        let height = 0;

        function resize() {
            const bounds = card.getBoundingClientRect();
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
            for (let index = 0; index < 12; index += 1) {
                particles.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    radius: 0.7 + Math.random() * 1.2,
                    speed: 0.04 + Math.random() * 0.08,
                    drift: (Math.random() - 0.5) * 0.08,
                    opacity: 0.08 + Math.random() * 0.1,
                });
            }
        }

        function animate() {
            context.clearRect(0, 0, width, height);
            particles.forEach(function (particle) {
                particle.y -= particle.speed;
                particle.x += particle.drift;
                if (particle.y < -4) particle.y = height + 4;
                if (particle.x < -4) particle.x = width + 4;
                if (particle.x > width + 4) particle.x = -4;
                context.beginPath();
                context.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                context.fillStyle = "rgba(220, 226, 224, " + particle.opacity + ")";
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
}());
