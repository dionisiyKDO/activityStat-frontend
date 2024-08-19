<script>
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

	let data = $state([]);
    let filteredData = $derived(
        data.filter(d => {
            const date = new Date(d.timestamp);
            d.date = date.toISOString().split('T')[0]; // create date string
            d.date = date; // create date string
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
        // Delete old chart if it exists
        d3.select("#chart").selectAll("*").remove();

        const container = d3.select("#container");
        margin = { top: 10, right: 30, bottom: 60, left: 60 };
        width = container.node().getBoundingClientRect().width - margin.left - margin.right;
        height = 400 - margin.top - margin.bottom;

        svg = d3.select("#chart")
            .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const sumstat = d3.group(filteredData, d => d.app); // group the data by app: I want to draw one line per app
        const color = d3.scaleOrdinal().range(['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999']); // create color palette for different lines

        const x = d3.scaleTime()
            .range([0, width])
            .domain(d3.extent(data, d => d.date));

        const y = d3.scaleLinear()
            .range([height, 0])
            .domain([0, d3.max(filteredData, d => d.duration)])
            .nice();

        const line = d3.line()
            .x(d => x(d.date))
            .y(d => y(d.duration));

        const xAxis = svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .style("font-size", "14px")
            .call(d3.axisBottom(x)
                .tickValues(x.ticks(d3.timeMonth.every(2))) // Display ticks every 2 months
                .tickFormat(d3.timeFormat("%b %Y"))) // Format the tick labels to show Month and Year
            .call(g => g.select(".domain").remove()) // Remove the x-axis line
            .selectAll(".tick line") // Select all tick lines
                .style("stroke-opacity", 0);

        const yAxis = svg.append("g")
            .style("font-size", "14px")
            .call(d3.axisLeft(y))
            .call(g => g.select(".domain").remove())
            .selectAll(".tick line") // Select all tick lines
                .style("stroke-opacity", 0); // Remove the y-axis line
        
        svg.selectAll(".tick text")
            .style("fill", "#777");

        // Add vertical gridlines
        const xGrid = svg.selectAll("xGrid")
            .data(x.ticks().slice(1, -1))
            .join("line")
            .attr("x1", d => x(d))
            .attr("x2", d => x(d))
            .attr("y1", 0)
            .attr("y2", height)
            .attr("stroke", "#e0e0e0")
            .attr("stroke-width", .5);
            
        // Add horizontal gridlines
        svg.selectAll("yGrid")
            .data(y.ticks())
            .join("line")
            .attr("x1", 0)
            .attr("x2", width)
            .attr("y1", d => y(d))
            .attr("y2", d => y(d))
            .attr("stroke", "#e0e0e0")
            .attr("stroke-width", .5)
        
        // Add Y-axis label
        svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left)
            .attr("x", 0 - (height / 2))
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .style("font-size", "14px")
            .style("fill", "#777")
            .style("font-family", "sans-serif")
            .text("Duration");


        // Add the line path
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
        


        const tooltipLine = svg.append('line');
        const tooltip = d3.select('#tooltip').style('opacity', 0)
            .style('position', 'absolute')
            .style('z-index', '10')
            .style('pointer-events', 'none')
            .style("background-color", "#1a1a1a")
            .style("border", "solid 1px #646cff")
            .style("color", "rgba(255, 255, 255, 0.87)")
            .style("padding", "5px")
            .style("border-radius", "2px")
            .style('box-shadow', '0 0 10px rgba(0, 0, 0, 0.1)');

        const listeningRect = svg.append('rect')
            .attr('width', width)
            .attr('height', height)
            .attr('opacity', 0)
            .on('mousemove', drawTooltip)
            .on('mouseout', removeTooltip);

        // Function to draw the tooltip
        function drawTooltip(event) {
            const [mouseXsvg, mouseYsvg] = d3.pointer(event); // Get mouse position
            const mouseX = event.clientX;
            const mouseY = event.clientY;
            const xDate = x.invert(mouseXsvg); // Find the x position in date
            const sumstatArray = Array.from(sumstat);

            // Get the closest data points to the mouse x position for each line
            const points = sumstatArray.map(([key, values]) => {
                const closestPoint = d3.least(values, d => Math.abs(x(d.date) - mouseXsvg));
                return {
                    app: key,
                    date: closestPoint.date,
                    duration: closestPoint.duration,
                    x: x(closestPoint.date),
                    y: y(closestPoint.duration)
                };
            });

            const tooltipWidth = tooltip.node().offsetWidth;
            const tooltipHeight = tooltip.node().offsetHeight;

            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            
            // Calculate tooltip position
            let tooltipLeft = mouseX + 20;
            let tooltipTop = mouseY - 40;

            // Adjust the position if the tooltip goes beyond the viewport
            if (tooltipLeft + tooltipWidth > viewportWidth) { 
                tooltipLeft = mouseX - tooltipWidth - 10; 
            }
            if (tooltipTop + tooltipHeight > viewportHeight) {
                tooltipTop = mouseY - tooltipHeight - 10;
            }

            tooltip
                .style("left", `${tooltipLeft}px`)
                .style("top", `${tooltipTop}px`)
                .style("opacity", 1);

            const tooltipContent = points.map(point => 
                `<div>
                    <strong>${point.app}</strong><br>
                    Date: ${d3.timeFormat("%b %d, %Y")(point.date)}<br>
                    Duration: ${point.duration} Hours
                </div>`
            ).join('<hr>');

            tooltip.html(tooltipContent);

            // Update tooltip line position
            tooltipLine
                .attr("x1", mouseXsvg)
                .attr("x2", mouseXsvg)
                .attr("y1", 0)
                .attr("y2", height)
                .attr("stroke", "#aaa")
                .attr("stroke-width", 1);
            }

        function removeTooltip() {
            tooltip.style("opacity", 0);
            tooltipLine.attr("stroke-width", 0); // Hide the tooltip line
        }

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
            <span>End Date: {end_date_input}</span>
        </div>
    </div>

    <svg id="chart"></svg>
    <div id="tooltip"></div >

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
