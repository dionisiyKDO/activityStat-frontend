<script>
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

	let data = $state([]);
    let filteredData = $derived(
        data.filter(d => {
            const date = new Date(d.timestamp);
            d.date = date.toISOString().split('T')[0]; // create date string
            return date >= new Date(start_date_input) && date <= new Date(end_date_input);
        })
    );
    async function fetchData() {
        const response = await fetch("/api/daily_app_usage/" + app);
        const r = JSON.parse(await response.json(),
                            (key, value) => typeof value === "number" ? Math.round(value * 100) / 100 : value); // round numbers to 2 decimals
        return r;
    }

    let app = $state("chrome.exe");
    let start_date_input = $state('2023-02-01');  // TODO: calculate start date automatically
    let end_date_input   = $state('2024-08-11');  // TODO: set end date to today 
    
    // TODO : rethink this variables
    let startDate = $derived(new Date(start_date_input));
    let endDate   = $derived(new Date(end_date_input));

    let minDate = startDate.getTime();
    let maxDate = endDate.getTime();
    let startDateNumeric = $state(startDate.getTime());
    let endDateNumeric   = $state(endDate.getTime());

    let svg, xScale, xAxis, width, height, margin = $state();

    // TODO : make input (selector) for avaible apps to include/exclude from the chart
    // TODO : Consider updating only the X-axis limits instead of fully redrawing the chart
    // TODO : add notice (2024-06-13 -- 2024-06-19 doesnt exist)
    // TODO Chart
        // TODO : fix chart to display zero usage hours between 13th and 20th, instead of a continuous line from 4h (13th) to 4h (20th)
        // TODO : add a ceiling for the chart Y-axis data (so X-axis limits dont change Y-axis range)

    onMount(() => {
        fetchData().then(r => {
            data = r;
            drawChart();
        });
    });

    function updateStartDate(event) {
        startDateNumeric = Number(event.target.value);
        start_date_input = new Date(startDateNumeric).toISOString().split('T')[0];
        drawChart();
    }

    function updateEndDate(event) {
        endDateNumeric = Number(event.target.value);
        end_date_input = new Date(endDateNumeric).toISOString().split('T')[0];
        drawChart();
    }

    function update(event) {
        fetchData().then(r => {
            data = r;
            drawChart();
        });
    }

    function drawChart() {
        const container = d3.select("#container");
        margin = {top: 10, right: 30, bottom: 60, left: 60};
        width = container.node().getBoundingClientRect().width - margin.left - margin.right;
        height = 400 - margin.top - margin.bottom;

        // Delete old chart if it exists
        d3.select("#chart").selectAll("*").remove();

        svg = d3.select("#chart")
            .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const sumstat = d3.group(filteredData, d => d.app); // group the data by app: I want to draw one line per app
        const color = d3.scaleOrdinal() // create color palette for different lines
            .range(['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999']);

        // Initialize xScale and xAxis
        xScale = d3.scaleTime()
            .domain(d3.extent(filteredData, function(d) { return new Date(d.timestamp); }))
            .range([0, width]);

        xAxis = d3.axisBottom(xScale)
            .tickFormat(d3.timeFormat("%Y-%m-%d"));

        svg.append("g")
            .attr("transform", `translate(0, ${height})`)
            .attr("class", "x-axis")
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

        const yAxis = d3.axisLeft(yScale);

        svg.append("g")
            .call(yAxis);

        // Draw the lines
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

    // for the future
    function updateXAxis() {
        // Update xScale domain based on new start and end dates
        xScale.domain([
            new Date(startDateNumeric), 
            new Date(endDateNumeric)
        ]);

        // Select and update the x-axis
        svg.select(".x-axis")
            .transition()
            .duration(1000)
            .call(xAxis);

        // Update the lines to reflect the new xScale
        svg.selectAll(".line")  // Make sure to select the correct paths
            .transition()
            .duration(1000)
            .attr("d", function(d){
                return d3.line()
                    .x(function(d) { return xScale(new Date(d.timestamp)); })
                    .y(function(d) { return yScale(+d.duration); })
                    (d[1]);
            });
    }
</script>

<div id="container">
    <div class="app"><input id="app" type="text" bind:value={app} onfocusout={update} /></div>
    <!-- 
    <input type="date" id="start" bind:value={startDate} />
    <input type="date" id="end" bind:value={endDate} /> 
    -->
    <div class="slider-container">
        <div class="dates">
            <input 
              type="range" 
              min={minDate} 
              max={maxDate} 
              bind:value={startDateNumeric} 
              oninput={updateStartDate} 
              class="slider" 
            />
            <span>Start Date: {start_date_input}</span>
        </div>
      
        <div class="dates">
            <input 
              type="range" 
              min={minDate} 
              max={maxDate} 
              bind:value={endDateNumeric} 
              oninput={updateEndDate} 
              class="slider" 
            />
            <span>Start Date: {start_date_input}</span>
        </div>
    </div>

    <svg id="chart"></svg>

</div>


<style>
    div {
        margin-bottom: 10px;
    }
    .app {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .app input {
        width: 60%;
        margin: 10px;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 1.2em;
        background-color: #222222;
    }
    .slider-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .dates {
        width: 40%;
        margin: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .dates input {
        width: 100%;
    }
</style>
