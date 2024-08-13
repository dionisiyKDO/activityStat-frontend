<script>
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

	let data = $state([]);
    let waiting = $state('Loading...');


    let app = $state("chrome.exe");
    let start_date = $state('2020-01-01');
    let end_date = $state('2024-08-11');
    let filteredData = $derived(
        data.filter(d => {
            const date = new Date(d.timestamp);
            d.date = date.toISOString().split('T')[0]; // create date string
            return date >= new Date(start_date) && date <= new Date(end_date);
        })
    );

    // TODO: make selector for apps, so i can fetch for different apps
    // TODO: change back to timescale. Now it scips dates
    // let chart = $derived(drawChart());

    async function fetchData() {
        const response = await fetch("/api/daily_app_usage/" + app);
        const r = JSON.parse( 
            await response.json(), // returns a promise
            (key, value) => typeof value === "number" ? Math.round(value * 100) / 100 : value // rounding
        );

        return r;
    }

    onMount(() => {
        fetchData().then(r => {
            data = r;
            drawChart();
        });
    });

    // TODO: в пробел, с 13 по 20 число, не показывается что 0 часов использовалось приложение, оно просто рисует линию с там 2 часа 13 часа до 4 часа 20 число, не видно нуля в неделю
    function drawChart() {
        // set the dimensions and margins of the graph
        const container = d3.select("#container");
        const margin = {top: 10, right: 30, bottom: 60, left: 60},
            width = container.node().getBoundingClientRect().width - margin.left - margin.right,
            height = 400 - margin.top - margin.bottom;

        // append the svg object to the body of the page
        d3.select("#chart").selectAll("*").remove();
        const svg = d3.select("#chart")
            .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // group the data: I want to draw one line per group
        const sumstat = d3.group(filteredData, d => d.app); // nest function allows to group the calculation per level of a factor

        // Add X axis --> it is a date format
        const x = d3.scaleTime()
            .domain(d3.extent(filteredData, function(d) { return new Date(d.timestamp); }))
            .range([0, width]);

        const xAxis = d3.axisBottom(x)
            // .ticks(3) // aim for around 10 ticks
            .tickFormat(d3.timeFormat("%Y-%m-%d"));

        svg.append("g")
            .attr("transform", `translate(0, ${height})`)
            .call(xAxis)
            .selectAll("text")                          // select all labels
                .attr("transform", "rotate(-20)")       // rotate selected labels
                .style("text-anchor", "end")            // make so end of the label is at the x-axis line (position anchor is at the end of the label)
                .style("font-size", "1.1em");

        // Add Y axis
        const y = d3.scaleLinear()
            .domain([0, d3.max(filteredData, function(d) { return +d.duration; })])
            .range([height, 0])
            .nice();

        svg.append("g")
            .call(d3.axisLeft(y));

        // color palette
        const color = d3.scaleOrdinal()
            .range(['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999']);

        // Draw the line
        svg.selectAll(".line")
            .data(sumstat)
            .join("path")
                .attr("fill", "none")
                .attr("stroke", function(d){ return color(d[0]); })
                .attr("stroke-width", 1.5)
                .attr("d", function(d){
                    return d3.line()
                        .x(function(d) { return x(new Date(d.timestamp)); })
                        .y(function(d) { return y(+d.duration); })
                        (d[1]);
                });
    }

    let startDate = $derived(new Date(start_date));
    let endDate = $derived(new Date(end_date));

    // Convert date to a numeric value for the range slider
    let minDate = new Date('2023-01-01').getTime(); // Minimum date
    let maxDate = new Date('2025-12-31').getTime(); // Maximum date
    let startDateNumeric = startDate.getTime();
    let endDateNumeric = endDate.getTime();

    // TODO: мб не перерисовывать полностью граф, а обновлять ось Х, левый правый лимит обновлять
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
