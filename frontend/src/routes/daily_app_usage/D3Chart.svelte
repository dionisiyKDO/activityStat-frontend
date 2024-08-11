<script>
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

    export let data;

    // TODO : Show titles of the apps (Client-Win64-Shipping.exe is fucking Wuthering Waves)
    // TODO : loading something for first request
    onMount(() => {
        // Setting up the SVG container dimensions
        const container = d3.select("#chart-container");
        const width = container.node().getBoundingClientRect().width;
        const height = 400;
        const margin = { top: 10, right: 60, bottom: 100, left: 60 };

        const svg = d3
            .select("#daily-app-usage-chart")
                .attr("viewBox", `0 0 ${width} ${height}`)
                .attr("transform", `translate(${0},${-margin.top})`)
                .append("g");
        
        // Parse the timestamps into date objects
        data.forEach(d => {
            d.date = new Date(d.timestamp);
        });

        // Create a scale for the x-axis (applications)
        const x = d3.scaleTime()
            .domain(d3.extent(data, d => d.date))
            .range([margin.left, width - margin.right])
            .nice();

        // Create a scale for the y-axis (duration)
        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.duration)])
            .range([height - margin.bottom, margin.top])
            .nice();

        // Add the x-axis to the SVG
        svg.append("g")
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%Y-%m-%d")))
            .selectAll("text")
                .attr("transform", "rotate(-40)")
                .style("text-anchor", "end")
                .style("font-size", "1.1em");

        // Add the y-axis to the SVG
        svg.append("g")
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y));

        // Add circles for each data point (for interactivity)
        svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.date))
            .attr("y", d => y(d.duration))
            .attr("width", (width - margin.right - margin.left) / data.length * 0.8) // set width based on the number of bars
            .attr("height", d => y(0) - y(d.duration))
            .attr("fill", "#e9e9e9")
            // .attr("transition", "all 0.5s ease") // add transition(check later)
            .on("mouseover", function(event, d) {
                tooltip
                    .transition()
                    .duration(200)
                    .style("opacity", 1);
                tooltip
                    .html(`Date: <strong>${d3.timeFormat("%Y-%m-%d")(d.date)}</strong><br>
                           App: <strong>${d.app}</strong><br>
                           Duration: <strong>${(d.duration).toFixed(2)}</strong> hours`)
                    .style("left", (event.pageX) + "px")
                    .style("top", (event.pageY - 28) + "px");
                d3.select(this)
                    .attr("fill", "#cacaca")
                    .attr("cursor", "pointer");
            })
            .on("mousemove", function(event) {
                tooltip
                    .style("top", `${event.pageY - 10}px`)
                    .style("left", `${event.pageX + 10}px`);
            })
            .on("mouseout", function(d) {
                tooltip
                    .transition()
                    .duration(500)
                    .style("opacity", 0);
                d3.select(this)
                    .attr("fill", "#e9e9e9")
                    .attr("cursor", "default");
            });
        
        // Add a tooltip
        const tooltip = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
                .style("position", "absolute")
                .style("background-color", "#1a1a1a")
                .style("border", "solid 1px #646cff")
                .style("color", "rgba(255, 255, 255, 0.87)")
                .style("padding", "5px")
                .style("border-radius", "2px")
                .style("opacity", 0)
                .style("pointer-events", "none"); // Prevent the tooltip from interfering with mouse events
                ;
    });
</script>

<div id="chart-container">
    <svg id="daily-app-usage-chart"></svg>
</div>

<style>
    svg {
        font: 10px sans-serif;
    }

    /* .axis path,
    .axis line {
        fill: none;
        shape-rendering: crispEdges;
    }
    .tooltip {
        position: absolute;
        text-align: center;
        width: auto;
        height: auto;
        padding: 5px;
        font: 12px sans-serif;
        background: lightsteelblue;
        border: 0px;
        border-radius: 8px;
        pointer-events: none;
    } */
</style>
