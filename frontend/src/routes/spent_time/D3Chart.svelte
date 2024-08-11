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
            .select("#spent-time-chart")                             // select the SVG element
                .attr("viewBox", `0 0 ${width} ${height}`)           // set scalable height and width
                .attr("transform", `translate(${0},${-margin.top})`) // move the group element
                .append("g");                                        // append a group element
        
        // Create a scale for the x-axis (applications)
        const x = d3.scaleBand()
            .domain(data.map(d => d.title))                          // select data
            .range([margin.left, width - margin.right])              // set range
            .padding(0.05);                                          // add padding

        // Create a scale for the y-axis (duration)
        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.duration)])              // select data
            .range([height - margin.bottom, margin.top])             // set range
            .nice();                                                 // set highest y value a nice round number 

        // Add the axises to the SVG
        // #region
        // Add the x-axis to the SVG
        svg.append("g")
            .attr("transform", `translate(0,${height - margin.bottom})`)    // y-axis position
            .call(d3.axisBottom(x))                                         // x-axis
            .selectAll("text")                          // select all labels
                .attr("transform", "rotate(-40)")       // rotate selected labels
                .style("text-anchor", "end")            // make so end of the label is at the x-axis line (position anchor is at the end of the label)
                .style("font-size", "1.1em");

        // Add the y-axis to the SVG
        svg.append("g")
            .attr("transform", `translate(${margin.left},0)`)   // x-axis position
            .call(d3.axisLeft(y));                              // y-axis                    
        // #endregion

        // Create the bars
        svg.selectAll(".bar")                           // select all (future) bars
            .data(data)                                 // bind data ('create' bars for each entrie in data)
            .enter().append("rect")                     // append a 'rect' for each entrie and for each rect:
                .attr("class", "bar")                       // add class 'bar'
                .attr("x", d => x(d.title))                   // set x position
                .attr("y", d => y(d.duration))              // set y position
                .attr("width", x.bandwidth())               // set width
                .attr("height", d => y(0) - y(d.duration))  // set height
                .attr("fill", "#e9e9e9")                    // set color
                .attr("transition", "all 0.5s ease")             // add transition
            .on("mouseover", function(event, d) {
                tooltip
                    .transition()
                    .duration(200)
                    .style("opacity", 1);
                tooltip
                    .html(`Title: <strong>${d.title}</strong><br>App: <strong>${d.app}</strong><br>Duration: <strong>${d.duration.toFixed(2)}</strong> hours`)
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
    <svg id="spent-time-chart"></svg>
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
