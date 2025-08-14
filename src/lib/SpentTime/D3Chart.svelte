<script lang="ts">
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

    export let data;

    // TODO : loading something for first request
    // TODO : Add notice (2024-06-13 -- 2024-06-19 doesnt exist)
    // TODO : add the ability to remove specific apps from the chart
    onMount(() => {
        const container = d3.select("#chart-container");
        const width = container.node().getBoundingClientRect().width;
        const height = 400;
        const margin = { top: 10, right: 60, bottom: 100, left: 60 };

        const filter_threshold = 50;

        const svg = d3
            .select("#spent-time-chart")                             // select the SVG element
                .attr("viewBox", `0 0 ${width} ${height}`)           // set scalable height and width
                .attr("transform", `translate(${0},${-margin.top})`) // move the group element
                .append("g");                                        // append a group element
        
        // Create a scale for the x-axis (applications)
        const xScale = d3.scaleBand()
            .domain(data.filter(d => d.duration > filter_threshold)
                .map(d => d.title))                                      // select titles to be present
            .range([margin.left, width - margin.right])                // set range
            .padding(0.05);                                            // add padding

        // Create a scale for the y-axis (duration)
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.duration)])              // select data
            .range([height - margin.bottom, margin.top])             // set range
            .nice();                                                 // set highest y value a nice round number 

        // Add the x-axis to the SVG
        const xAxis = d3.axisBottom(xScale)
        svg.append("g")
            .attr("transform", `translate(0,${height - margin.bottom})`)    // y-axis position
            .call(xAxis)                                                    // x-axis
            .selectAll("text")                          // select all labels
                .attr("transform", "rotate(-40)")       // rotate selected labels
                .style("text-anchor", "end")            // make so end of the label is at the x-axis line (position anchor is at the end of the label)
                .style("font-size", "1.1em");

        // Add the y-axis to the SVG
        const yAxis = d3.axisLeft(yScale)
        svg.append("g")
            .attr("transform", `translate(${margin.left},0)`)   // x-axis position
            .call(yAxis);                                       // y-axis                    

        // Create the bars
        svg.selectAll(".bar")                                       // select all (future) bars
            .data(data.filter(d => d.duration > filter_threshold))  // bind data ('create' bars for each entrie in data)
            .enter().append("rect")                                 // append a 'rect' for each entrie and for each rect:
                .attr("class", "bar")                                   // add class 'bar'
                .attr("x", d => xScale(d.title))                          // set x position
                .attr("y", d => yScale(d.duration))                     // set y position
                .attr("width", xScale.bandwidth())                      // set width
                .attr("height", d => yScale(0) - yScale(d.duration))    // set height
                .attr("fill", "#e9e9e9")                                // set color
                .attr("transition", "all 0.5s ease")                    // add transition
            .on("mouseover", function(event, d) {
                tooltip
                    .transition()
                    .duration(200)
                    .style("opacity", 1);
                tooltip
                    .style("left", (event.pageX) + "px")
                    .style("top", (event.pageY - 28) + "px")
                    .html(`Title: <strong>${d.title}</strong><br>App: <strong>${d.app}</strong><br>Duration: <strong>${d.duration.toFixed(2)}</strong> hours`);
                d3.select(this)
                    .attr("fill", "#cacaca")
                    .attr("cursor", "pointer");
            })
            .on("mousemove", function(event) {
                tooltip
                    .style("top", `${event.pageY - 10}px`)
                    .style("left", `${event.pageX + 10}px`);
            })
            .on("mouseleave", function(d) {
                tooltip
                    .transition()
                    .duration(500)
                    .style("opacity", 0);
                d3.select(this)
                    .attr("fill", "#e9e9e9")
                    .attr("cursor", "default");
            });
        
        const tooltip = d3.select("#bar-tooltip")
            .style("position", "absolute")
            .style("background-color", "#1a1a1a")
            .style("border", "solid 1px #646cff")
            .style("color", "rgba(255, 255, 255, 0.87)")
            .style("padding", "5px")
            .style("border-radius", "2px")
            .style("opacity", 0)
            .style("pointer-events", "none"); // Prevent the tooltip from interfering with mouse events
    });
</script>


<div id="chart-container">
    <svg id="spent-time-chart"></svg>
    <div id="bar-tooltip" class="tooltip"></div>
</div>


<style>
    svg {
        font-size: 32px;
    }
</style>
