<script>
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

	let data = $state([]);
    let filteredData = $derived(
        data.filter(d => {
            const date = new Date(d.timestamp);
            d.date = date;
            return date >= new Date(start_date_input) && date <= new Date(end_date_input);
        })
    );
    
    let app = $state("chrome.exe");
    let start_date_input = $state('1999-01-01');
    let end_date_input   = $state('2050-01-01');
    
    let startDate = $derived(new Date(start_date_input));
    let endDate   = $derived(new Date(end_date_input));

    let minDate = startDate.getTime();
    let maxDate = endDate.getTime();
    let startDateNumeric = $state(startDate.getTime());
    let endDateNumeric   = $state(endDate.getTime());

    let svgC, sumstat, color, xCScale, xCAxis, yCScale, yCAxis, widthC, heightC, marginC = $state();
    let svgB, xBScale, xBAxis, widthB, heightB, marginB = $state();
    
    marginC = { top: 10, right: 30, bottom: 30, left: 60 };
    marginB = { top: 0,  right: 30, bottom: 25, left: 60 };

    // TODO margin and consts move here, brush consts calc from there

    // TODO : make input (selector) for avaible apps to include/exclude from the chart
    // TODO : Consider updating only the X-axis limits instead of fully redrawing the chart
    // TODO : add notice (2024-06-13 -- 2024-06-19 doesnt exist)
    // TODO Chart
        // TODO : fix chart to display zero usage hours between 13th and 20th, instead of a continuous line from 4h (13th) to 4h (20th)
        // TODO : add a ceiling for the chart Y-axis data (so X-axis limits dont change Y-axis range)
        // TODO : remove apps from legends, so their lines wouldnt be visible

    async function fetchData() {
        const response = await fetch("/api/daily_app_usage/" + app);
        const roundedData = JSON.parse(await response.json(), (key, value) => 
            typeof value === "number" ? Math.round(value * 100) / 100 : value
        ); // round numbers to 2 decimals
        data = roundedData;
        return roundedData;
    }

    onMount(() => {
        getData()
    });

    function getData(event) {
        fetchData().then(r => {
            // TODO : look into updating start_date_input and end_date_input with the new data
            // [start_date_input, end_date_input] = d3.extent(data, d => d.date.toISOString().split('T')[0]);
            start_date_input = '1999-01-01';
            end_date_input   = '2050-01-01';
            drawChart();
            drawBrush();
        });
    }

    function drawChart() {
        // Delete old chart if it exists
        d3.select("#chart").selectAll("*").remove();
        // #region
        const container = d3.select("#container");
        widthC  = container.node().getBoundingClientRect().width - marginC.left - marginC.right;
        heightC = 400 - marginC.top - marginC.bottom;

        svgC = d3.select("#chart")
            .attr("viewBox", `0 0 ${widthC + marginC.left + marginC.right} ${heightC + marginC.top + marginC.bottom}`)
            .append("g")
            .attr("transform", `translate(${marginC.left},${marginC.top})`);

        // Define the clipPath
        svgC.append("defs")
            .append("clipPath")
            .attr("id", "clip")
            .append("rect")
            .attr("width", widthC)
            .attr("height", heightC);

        sumstat = d3.group(filteredData, d => d.app);
        color = d3.scaleOrdinal().range(['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999']);

        xCScale = d3.scaleTime()
            .range([0, widthC])
            .domain(d3.extent(filteredData, d => d.date));

        yCScale = d3.scaleLinear()
            .range([heightC, 0])
            .domain([0, d3.max(data, d => d.duration)]) 
            .nice();

        xCAxis = svgC.append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0,${heightC})`)
            .style("font-size", "14px")
            .call(d3.axisBottom(xCScale)
                .tickValues(xCScale.ticks(d3.timeMonth.every(2))) // Display ticks every 2 months
                .tickFormat(d3.timeFormat("%b %Y"))) // Format the tick labels to show Month and Year
            .call(g => g.select(".domain").remove()) // Remove the x-axis line
            .selectAll(".tick line") // Select all tick lines
                .style("stroke-opacity", 0);

        yCAxis = svgC.append("g")
            .attr("class", "y-axis")
            .style("font-size", "14px")
            .call(d3.axisLeft(yCScale))
            .call(g => g.select(".domain").remove())
            .selectAll(".tick line") // Select all tick lines
                .style("stroke-opacity", 0); // Remove the y-axis line
        
        svgC.selectAll(".tick text")
            .style("fill", "#777");

        // Add vertical gridlines
        const xCGrid = svgC.selectAll("xGrid")
            .data(xCScale.ticks().slice(1, -1))
            .join(
                enter => enter.append("line")
                    .attr("class", "x-grid")
                    .attr("y1", 0)
                    .attr("y2", heightC)
                    .attr("stroke", "#e0e0e0")
                    .attr("stroke-width", .5)
                    .attr("stroke-opacity", .33)
                    .attr("x1", d => xCScale(d))
                    .attr("x2", d => xCScale(d)),
                update => update
                    .transition()
                    .duration(0)
                    .attr("x1", d => xCScale(d))
                    .attr("x2", d => xCScale(d)),
                exit => exit.remove()
            );
            
        // Add horizontal gridlines
        const yCGrid = svgC.selectAll("yGrid")
            .data(yCScale.ticks())
            .join("line")
            .attr("x1", 0)
            .attr("x2", widthC)
            .attr("y1", d => yCScale(d))
            .attr("y2", d => yCScale(d))
            .attr("stroke", "#e0e0e0")
            .attr("stroke-width", .5)
            .attr("stroke-opacity", .33);
        
        // Add Y-axis label
        svgC.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - marginC.left)
            .attr("x", 0 - (heightC / 2))
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .style("font-size", "14px")
            .style("fill", "#777")
            .style("font-family", "sans-serif")
            .text("Duration");

        // Add border around the chart area
        svgC.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", widthC)
            .attr("height", heightC)
            .attr("stroke", "#777")
            .attr("fill", "none");

        // #endregion

        // Add the line path
        svgC.selectAll(".line")
            .data(sumstat, d => d[0]) // Use the app name or unique identifier as the key
            .join(
                enter => enter.append("path") // Handle entering elements
                    .attr("class", "line")
                    .attr("fill", "none")
                    .attr("stroke", d => color(d[0]))
                    .attr("stroke-width", 1.5)
                    .attr("clip-path", "url(#clip)") 
                    .attr("d", d => d3.line()
                        .x(d => xCScale(new Date(d.timestamp)))
                        .y(d => yCScale(+d.duration))
                        (d[1])),
                update => update.transition() // Handle updating elements
                    .duration(0) // Transition duration in ms
                    .attr("clip-path", "url(#clip)")
                    .attr("d", d => d3.line()
                        .x(d => xCScale(new Date(d.timestamp)))
                        .y(d => yCScale(+d.duration))
                        (d[1])),
                exit => exit.remove() // Handle exiting elements
            );
        
        // #region

        const tooltipLine = svgC.append('line');
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

        const listeningRect = svgC.append('rect')
            .attr('width', widthC)
            .attr('height', heightC)
            .attr('opacity', 0)
            .on('mousemove', drawTooltip)
            .on('mouseout', removeTooltip);

        // Function to draw the tooltip
        // TODO : Color the tooltip text based on the app line color
        // TODO : Draw circle on the closest data point when the mouse hovers over the line
        function drawTooltip(event) {
            const [mouseXsvg, mouseYsvg] = d3.pointer(event); // Get mouse position
            const mouseX = event.clientX;
            const mouseY = event.clientY;
            const xDate = xCScale.invert(mouseXsvg); // Find the x position in date
            const sumstatArray = Array.from(sumstat);

            // Get the closest data points to the mouse x position for each line
            const points = sumstatArray.map(([key, values]) => {
                const closestPoint = d3.least(values, d => Math.abs(xCScale(d.date) - mouseXsvg));
                return {
                    app: key,
                    date: closestPoint.date,
                    duration: closestPoint.duration,
                    x: xCScale(closestPoint.date),
                    y: yCScale(closestPoint.duration)
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

            // TODO : tooltip date only once, color based on app, highlight the max value
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
                .attr("y2", heightC)
                .attr("stroke", "#aaa")
                .attr("stroke-width", 1)
                .attr("stroke-opacity", .66);
            }

        function removeTooltip() {
            tooltip.style("opacity", 0);
            tooltipLine.attr("stroke-width", 0); // Hide the tooltip line
        }
        // #endregion
    }
        
    function updateChart() {
        const newDomain = [new Date(start_date_input), new Date(end_date_input)];

        // Update the x scale domain
        xCScale.domain(newDomain);

        const dateRangeInDays = d3.timeDay.count(xCScale.domain()[0], xCScale.domain()[1]);
        console.log(dateRangeInDays);
        

        // Set the tick interval based on the date range in days
        let tickInterval;
        if (dateRangeInDays > 365 * 5) { // If the range is greater than 5 years
            tickInterval = d3.timeYear.every(1); // Display ticks every year
        } else if (dateRangeInDays > 365 * 2) { // If the range is between 2 and 5 years
            tickInterval = d3.timeMonth.every(6); // Display ticks every 6 months
        } else if (dateRangeInDays > 365) { // If the range is between 1 and 2 years
            tickInterval = d3.timeMonth.every(2); // Display ticks every 3 months
        } else if (dateRangeInDays > 180) { // If the range is between 6 months and 1 year
            tickInterval = d3.timeMonth.every(1); // Display ticks every month
        } else if (dateRangeInDays > 90) { // If the range is between 3 and 6 months
            tickInterval = d3.timeWeek.every(2); // Display ticks every 2 weeks
        } else if (dateRangeInDays > 30) { // If the range is between 1 and 3 months
            tickInterval = d3.timeWeek.every(1); // Display ticks every week
        } else if (dateRangeInDays > 10) { // If the range is between 10 days and 1 month
            tickInterval = d3.timeDay.every(2); // Display ticks every 2 days
        } else {
            tickInterval = d3.timeDay.every(1); // For very short ranges, display ticks every day
        }

        // Update the x-axis
        svgC.select(".x-axis") // Ensure you're selecting the axis group by class or ID
            .attr("class", "x-axis")
            .attr("transform", `translate(0,${heightC})`)
            .style("font-size", "14px")
            .transition()
            .duration(0)
            .call(d3.axisBottom(xCScale)
                .tickValues(xCScale.ticks(tickInterval)) // Display ticks every 2 months
                .tickFormat(d3.timeFormat("%b %Y"))) // Format the tick labels to show Month and Year;
            .call(g => g.select(".domain").remove()) // Remove the x-axis line
            .selectAll(".tick line") // Select all tick lines
                .style("stroke-opacity", 0)
                


        // Update the vertical gridlines
        svgC.selectAll(".x-grid")
            .data(xCScale.ticks())
            .join(
                enter => enter.append("line")
                    .attr("class", "x-grid")
                    .attr("y1", 0)
                    .attr("y2", heightC)
                    .attr("stroke", "#e0e0e0")
                    .attr("stroke-width", .5)
                    .attr("stroke-opacity", .33),
                update => update
                    .transition()
                    .duration(0)
                    .attr("x1", d => xCScale(d))
                    .attr("x2", d => xCScale(d)),
                exit => exit.remove()
            );

        svgC.selectAll(".tick text")
            .style("fill", "#777");

        // Update the lines with the new x scale
        svgC.selectAll(".line")
            .data(sumstat) // Use the app name or unique identifier as the key
            .join(
                enter => enter.append("path") // Handle entering elements
                    .attr("class", "line")
                    .attr("fill", "none")
                    .attr("stroke", d => color(d[0]))
                    .attr("stroke-width", 1.5)
                    .attr("clip-path", "url(#clip)")
                    .attr("d", d => d3.line()
                        .x(d => xCScale(new Date(d.timestamp)))
                        .y(d => yCScale(+d.duration))
                        (d[1])),
                update => update.transition() // Handle updating elements
                    .duration(0) // Transition duration in ms
                    .attr("clip-path", "url(#clip)")
                    .attr("d", d => d3.line()
                        .x(d => xCScale(new Date(d.timestamp)))
                        .y(d => yCScale(+d.duration))
                        (d[1])),
                exit => exit.remove() // Handle exiting elements
            );
    }


    function drawBrush() {
        // TODO : double click to reset start and end date
        
        // Delete old chart if it exists
        d3.select("#brush").selectAll("*").remove();

        const container = d3.select("#container");
        widthB = container.node().getBoundingClientRect().width - marginB.left - marginB.right;
        heightB = 70 - marginB.top - marginB.bottom;

        svgB = d3.select("#brush")
            .attr("viewBox", `0 0 ${widthB + marginB.left + marginB.right} ${heightB + marginB.top + marginB.bottom}`)
            .append("g")
            .attr("transform", `translate(${marginB.left},${marginB.top})`);

        xBScale = d3.scaleTime()
            .range([0, widthB])
            .domain(d3.extent(data, d => d.date));

        xBAxis = svgB.append("g")
            .attr("transform", `translate(0,${heightB})`)
            .style("font-size", "14px")
            .call(d3.axisBottom(xBScale)
                .tickValues(xBScale.ticks(d3.timeMonth.every(2))) // Display ticks every 2 months
                .tickFormat(d3.timeFormat("%b %Y"))) // Format the tick labels to show Month and Year
            .call(g => g.select(".domain").remove()) // Remove the x-axis line
            .selectAll(".tick line") // Select all tick lines
                .style("stroke-opacity", 0);

        svgB.selectAll(".tick text")
            .style("fill", "#777");

        // Add vertical gridlines
        const xBGrid = svgB.selectAll("xGrid")
            .data(xBScale.ticks())
            .attr("class", "x-grid")
            .join("line")
            .attr("x1", d => xBScale(d))
            .attr("x2", d => xBScale(d))
            .attr("y1", 0)
            .attr("y2", heightB)
            .attr("stroke", "#e0e0e0")
            .attr("stroke-width", .5)
            .attr("stroke-opacity", .33);

        // Add border around the chart area
        svgB.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", widthB)
            .attr("height", heightB)
            .attr("stroke", "#777")
            .attr("fill", "none");

        // Create the brush
        const brush = d3.brushX()
            .extent([[0, 0], [widthB, heightB]])
            .on("brush end", brushed);

        // Add the brush to the SVG
        svgB.append('g')
            .attr('class', 'brush')
            .call(brush);

        // Brush event handler
        function brushed({ selection }) {
            if (selection) {
                const [x0, x1] = selection.map(xBScale.invert);                    
                start_date_input = new Date(x0).toISOString().split('T')[0];
                end_date_input = new Date(x1).toISOString().split('T')[0];
                updateChart();
            }
        }
    }
</script>

<div id="container">
    <div class="app"><input id="app" type="text" bind:value={app} onfocusout={getData} /></div>
    <div class="date-container">
        <span>Start Date: {start_date_input}</span>
        <span>End Date: {end_date_input}</span>
    </div>

    <svg id="brush"></svg>
    <svg id="chart"></svg>
    <div id="tooltip"></div>
</div>


<style>
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
    .date-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        font-size: 1.2em;
        padding: 20px;
    }
</style>
