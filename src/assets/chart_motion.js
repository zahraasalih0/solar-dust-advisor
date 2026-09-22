(function () {
    const animatedIds = ["forecast-chart", "cumulative-loss-chart"];

    function attachChartMotion() {
        animatedIds.forEach(function (id) {
            const graph = document.getElementById(id);
            if (!graph || graph.dataset.motionReady === "true") return;

            graph.on("plotly_afterplot", function () {
                const plotContainer = graph.querySelector(".plot-container");
                if (!plotContainer) return;
                plotContainer.classList.remove("chart-reveal-left");
                void plotContainer.offsetWidth;
                plotContainer.classList.add("chart-reveal-left");
            });

            if (id === "forecast-chart") {
                graph.on("plotly_hover", function (event) {
                    if (event && event.points && event.points.length) {
                        Plotly.restyle(graph, {"marker.size": 10}, [event.points[0].curveNumber]);
                    }
                });
                graph.on("plotly_unhover", function () {
                    Plotly.restyle(graph, {"marker.size": 6});
                });
            }

            graph.dataset.motionReady = "true";
        });
    }

    document.addEventListener("DOMContentLoaded", attachChartMotion);
    new MutationObserver(attachChartMotion).observe(document.body, {childList: true, subtree: true});
}());
