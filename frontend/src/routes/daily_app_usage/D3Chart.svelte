<script>
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

	let data = $state([]);

    let app = $state("chrome.exe");
    let start_date = $state('2023-02-01');  // TODO: calculate start date automatically
    let end_date = $state('2024-08-11');    // TODO: set end date to today 
    
    let filteredData = $derived(
        data.filter(d => {
            const date = new Date(d.timestamp);
            d.date = date.toISOString().split('T')[0]; // create date string
            return date >= new Date(start_date) && date <= new Date(end_date);
        })
    );

    let startDate = $derived(new Date(start_date));
    let endDate = $derived(new Date(end_date));

    let minDate = new Date(start_date).getTime(); // Minimum date
    let maxDate = new Date(end_date).getTime(); // Maximum date
    let startDateNumeric = startDate.getTime();
    let endDateNumeric = endDate.getTime();

    // TODO: make input (selector) for avaible apps to include/exclude from the chart
    // TODO: Consider updating only the X-axis limits instead of fully redrawing the chart
    // TODO : Add notice (2024-06-13 -- 2024-06-19 doesnt exist)
        // TODO: Fix chart to display zero usage hours between 13th and 20th, instead of a continuous line from 4h (13th) to 4h (20th)

    function updateStartDate(event) {
        startDateNumeric = Number(event.target.value);
        start_date = new Date(startDateNumeric).toISOString().split('T')[0];
        drawChart();
    }

    function updateEndDate(event) {
        endDateNumeric = Number(event.target.value);
        end_date = new Date(endDateNumeric).toISOString().split('T')[0];
        drawChart();
    }

    function update(event) {
        fetchData().then(r => {
            data = r;
            drawChart();
        });
    }

    onMount(() => {
        fetchData().then(r => {
            data = r;
            drawChart();
        });
    });

    function drawChart() {
        const container = d3.select("#container");
        const margin = {top: 10, right: 30, bottom: 60, left: 60};
        const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
        const height = 400 - margin.top - margin.bottom;

        // delete old chart
        d3.select("#chart").selectAll("*").remove();

        const svg = d3.select("#chart")
            .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const sumstat = d3.group(filteredData, d => d.app); // group the data by app: I want to draw one line per app
        const color = d3.scaleOrdinal() // create color palette for different lines
            .range(['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999']);

        // xAxis
        const xScale = d3.scaleTime()
            .domain(d3.extent(filteredData, function(d) { return new Date(d.timestamp); }))
            .range([0, width]);

        const xAxis = d3.axisBottom(xScale)
            .tickFormat(d3.timeFormat("%Y-%m-%d"));

        svg.append("g")
            .attr("transform", `translate(0, ${height})`)
            .call(xAxis)
            .selectAll("text")
                .attr("transform", "rotate(-20)")
                .style("text-anchor", "end")
                .style("font-size", "1.1em");

        // yAxis
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(filteredData, function(d) { return +d.duration; })])
            .range([height, 0])
            .nice();

        const yAxis = d3.axisLeft(yScale)

        svg.append("g")
            .call(yAxis);

        // Draw the line
        svg.selectAll(".line")
            .data(sumstat)
            .join("path")
                .attr("fill", "none")
                .attr("stroke", function(d){ return color(d[0]); })
                .attr("stroke-width", 1.5)
                .attr("d", function(d){
                    return d3.line()
                        .x(function(d) { return xScale(new Date(d.timestamp)); })
                        .y(function(d) { return yScale(+d.duration); })
                        (d[1]);
                });
    }

    async function fetchData() {
        const response = await fetch("/api/daily_app_usage/" + app);
        const r = JSON.parse( 
            await response.json(),
            (key, value) => typeof value === "number" ? Math.round(value * 100) / 100 : value // round numbers to 2 decimals
        );

        return r;
    }
</script>

<div id="container">
    <input id="app" type="text" bind:value={app} onfocusout={update} />
    <!-- <input type="date" id="start" bind:value={startDate} />
    <input type="date" id="end" bind:value={endDate} /> -->
    <div class="slider-container">
        <input 
          type="range" 
          min={minDate} 
          max={maxDate} 
          bind:value={startDateNumeric} 
          oninput={updateStartDate} 
          class="slider" 
        />
      
        <input 
          type="range" 
          min={minDate} 
          max={maxDate} 
          bind:value={endDateNumeric} 
          oninput={updateEndDate} 
          class="slider" 
        />
      
        <div class="dates">
          <span>Start Date: {start_date}</span>
          <span>End Date: {end_date}</span>
        </div>
      </div>
    <!-- <button onclick={update}>Update</button> -->
    <svg id="chart"></svg>
</div>

<style>
    svg {
        font: 10px sans-serif;
    }
    div {
        margin-bottom: 10px;
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
