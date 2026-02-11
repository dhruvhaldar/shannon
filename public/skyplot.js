function drawSkyplot(points) {
    const width = 400;
    const height = 400;
    const margin = 40;
    const radius = Math.min(width, height) / 2 - margin;

    // Clear previous if any (though innerHTML cleared in index.html)
    // But d3 might append to existing.
    // The calling code clears it: document.getElementById('skyplot').innerHTML = '';

    const svg = d3.select("#skyplot")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width/2},${height/2})`);

    // Scale for radius (Elevation)
    // Domain [0, 90], Range [radius, 0] (0 el is at radius, 90 el is at 0)
    const rScale = d3.scaleLinear()
        .domain([0, 90])
        .range([radius, 0]);

    // Draw grid circles
    const grids = [0, 30, 60];
    svg.selectAll(".grid-circle")
        .data(grids)
        .enter().append("circle")
        .attr("class", "grid-circle")
        .attr("r", d => rScale(d))
        .style("fill", "none")
        .style("stroke", "#ccc")
        .style("stroke-dasharray", "3,3");

    // Draw axis lines (N, E, S, W)
    const angles = [0, 90, 180, 270];
    const labels = ["N", "E", "S", "W"];

    svg.selectAll(".axis-line")
        .data(angles)
        .enter().append("line")
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", d => rScale(0) * Math.sin(d * Math.PI / 180))
        .attr("y2", d => -rScale(0) * Math.cos(d * Math.PI / 180))
        .style("stroke", "#ccc");

    // Add labels
    svg.selectAll(".label")
        .data(labels)
        .enter().append("text")
        .attr("x", (d, i) => (radius + 15) * Math.sin(angles[i] * Math.PI / 180))
        .attr("y", (d, i) => -(radius + 15) * Math.cos(angles[i] * Math.PI / 180))
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .text(d => d)
        .style("font-size", "12px")
        .style("fill", "#333");

    // Line generator
    const line = d3.line()
        .x(d => rScale(d.el) * Math.sin(d.az * Math.PI / 180))
        .y(d => -rScale(d.el) * Math.cos(d.az * Math.PI / 180));

    // Draw path
    svg.append("path")
        .datum(points)
        .attr("fill", "none")
        .attr("stroke", "blue")
        .attr("stroke-width", 2)
        .attr("d", line);

    // Draw AOS (first)
    svg.append("circle")
        .attr("cx", rScale(points[0].el) * Math.sin(points[0].az * Math.PI / 180))
        .attr("cy", -rScale(points[0].el) * Math.cos(points[0].az * Math.PI / 180))
        .attr("r", 4)
        .style("fill", "green");

    svg.append("text")
        .attr("x", rScale(points[0].el) * Math.sin(points[0].az * Math.PI / 180) + 5)
        .attr("y", -rScale(points[0].el) * Math.cos(points[0].az * Math.PI / 180) - 5)
        .text("AOS")
        .style("font-size", "10px")
        .style("fill", "green");

    // Draw LOS (last)
    const last = points[points.length-1];
    svg.append("circle")
        .attr("cx", rScale(last.el) * Math.sin(last.az * Math.PI / 180))
        .attr("cy", -rScale(last.el) * Math.cos(last.az * Math.PI / 180))
        .attr("r", 4)
        .style("fill", "red");

    svg.append("text")
        .attr("x", rScale(last.el) * Math.sin(last.az * Math.PI / 180) + 5)
        .attr("y", -rScale(last.el) * Math.cos(last.az * Math.PI / 180) - 5)
        .text("LOS")
        .style("font-size", "10px")
        .style("fill", "red");
}
