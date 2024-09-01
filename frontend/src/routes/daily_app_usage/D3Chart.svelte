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
    
    let app = $state("test.exe");
    let start_date_input = $state('1999-01-01');
    let end_date_input   = $state('2050-01-01');
    let notice = $state('(2024-06-13 -- 2024-06-19 doesnt exist)');
    
    let app_names = $state([]);

    let startDate = $derived(new Date(start_date_input));
    let endDate   = $derived(new Date(end_date_input));

    let minDate = startDate.getTime();
    let maxDate = endDate.getTime();
    let startDateNumeric = $state(startDate.getTime());
    let endDateNumeric   = $state(endDate.getTime());

    let svgC, sumstat, color, xCScale, xCAxis, yCScale, yCAxis, widthC, heightC, marginC, circles = $state();
    let svgB, xBScale, xBAxis, widthB, heightB, marginB = $state();
    
    marginC = { top: 10, right: 30, bottom: 30, left: 60 };
    marginB = { top: 0,  right: 30, bottom: 25, left: 60 };

    let animDuration = 0;


    async function fetchAppList() {
        try {
            const response = await fetch("/api/app_list/");
            const json = await response.json();
            app_names = json;
            console.log('app_names', app_names);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }
    
    async function fetchData() {
        const response = await fetch("/api/daily_app_usage/" + app);
        const json = await response.json();
        console.log('data', json);
        const roundedData = JSON.parse(json, (key, value) => 
            typeof value === "number" ? Math.round(value * 100) / 100 : value
        ); // round numbers to 2 decimals
        data = roundedData;
        return roundedData;
    }

    onMount(() => {
        fetchAppList();
        getData();
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
        d3.select("#chart").selectAll("*").remove();

        const container = d3.select("#container");
        widthC  = container.node().getBoundingClientRect().width - marginC.left - marginC.right;
        heightC = 400 - marginC.top - marginC.bottom;

        svgC = d3.select("#chart")
            .attr("viewBox", `0 0 ${widthC + marginC.left + marginC.right} ${heightC + marginC.top + marginC.bottom}`)
            .append("g")
            .attr("transform", `translate(${marginC.left},${marginC.top})`);

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
                .tickValues(xCScale.ticks(d3.timeMonth.every(2)))
                .tickFormat(d3.timeFormat("%b %Y")))
            .call(g => g.select(".domain").remove())
            .selectAll(".tick line")
                .style("stroke-opacity", 0);

        yCAxis = svgC.append("g")
            .attr("class", "y-axis")
            .style("font-size", "14px")
            .call(d3.axisLeft(yCScale))
            .call(g => g.select(".domain").remove())
            .selectAll(".tick line")
                .style("stroke-opacity", 0);
        
        svgC.selectAll(".tick text")
            .style("fill", "#777");

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
                    .duration(animDuration)
                    .attr("x1", d => xCScale(d))
                    .attr("x2", d => xCScale(d)),
                exit => exit.remove()
            );

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

        svgC.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", widthC)
            .attr("height", heightC)
            .attr("stroke", "#777")
            .attr("fill", "none");

        svgC.selectAll(".line")
            .data(sumstat, d => d[0])
            .join(
                enter => enter.append("path")
                    .attr("class", "line")
                    .attr("fill", "none")
                    .attr("stroke", d => color(d[0]))
                    .attr("stroke-width", 1.5)
                    .attr("clip-path", "url(#clip)") 
                    .attr("d", d => d3.line()
                        .x(d => xCScale(new Date(d.timestamp)))
                        .y(d => yCScale(+d.duration))
                        (d[1])),
                update => update.transition()
                    .duration(animDuration)
                    .attr("clip-path", "url(#clip)")
                    .attr("d", d => d3.line()
                        .x(d => xCScale(new Date(d.timestamp)))
                        .y(d => yCScale(+d.duration))
                        (d[1])),
                exit => exit.remove()
            );

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

        function drawTooltip(event) {
            const [mouseXsvg, mouseYsvg] = d3.pointer(event);
            const mouseX = event.clientX;
            const mouseY = event.clientY;
            const xDate = xCScale.invert(mouseXsvg);
            const sumstatArray = Array.from(sumstat);

            // Get the closest data points to the mouse x position for each line
            const points = sumstatArray.map(([key, values]) => {
                const closestPoint = d3.least(values, d => Math.abs(xCScale(d.date) - mouseXsvg));
                return {
                    app: key,
                    date: closestPoint.date,
                    duration: closestPoint.duration,
                    x: xCScale(closestPoint.date),
                    y: yCScale(closestPoint.duration),
                    color: color(key)
                };
            });

            const tooltipWidth = tooltip.node().offsetWidth;
            const tooltipHeight = tooltip.node().offsetHeight;
            
            let tooltipLeft = mouseX + 20;
            let tooltipTop = mouseY - 40;

            // Adjust the position if the tooltip goes beyond the viewport
            if (tooltipLeft + tooltipWidth > window.innerWidth) { 
                tooltipLeft = mouseX - tooltipWidth - 10; 
            }
            if (tooltipTop + tooltipHeight > window.innerHeight) {
                tooltipTop = mouseY - tooltipHeight - 10;
            }

            tooltip
                .style("left", `${tooltipLeft}px`)
                .style("top", `${tooltipTop}px`)
                .style("opacity", 1);

            let tooltipContent = `
                <div>
                    <strong>Date: </strong> ${d3.timeFormat("%b %d, %Y")(points[0].date)}<br><hr>
                </div>`;
            tooltipContent = tooltipContent + points.map(point => 
                `<div>
                    <strong style="color:${point.color}"> ${point.app} </strong> <br>
                    Duration: ${point.duration === Math.max(...points.map(point => point.duration)) ? `<strong style="font-weight: 600; color: white">${point.duration} Hours</strong>` : `${point.duration} Hours`}
                </div>`
            ).join('<br>');
            tooltip.html(tooltipContent);

            tooltipLine
                .attr("x1", mouseXsvg)
                .attr("x2", mouseXsvg)
                .attr("y1", 0)
                .attr("y2", heightC)
                .attr("stroke", "#aaa")
                .attr("stroke-width", 1)
                .attr("stroke-opacity", .66);
            
            circles = svgC.selectAll(".tooltip-circle")
                .data(points, d => d.app);

            // Remove any existing circles that are no longer needed
            circles.exit().remove();

            // Update existing circles
            circles
                .attr("cx", d => d.x)
                .attr("cy", d => d.y)
                .attr("r", 4)
                .attr("fill", d => d.color);

            // Add new circles
            circles.enter()
                .append("circle")
                .attr("class", "tooltip-circle")
                .attr("cx", d => d.x)
                .attr("cy", d => d.y)
                .attr("r", 4)
                .attr("fill", d => d.color);
            }

        function removeTooltip() {
            tooltip.style("opacity", 0);
            tooltipLine.attr("stroke-width", 0);
            svgC.selectAll(".tooltip-circle").remove();
        }
    }
        
    function updateChart() {
        const newDomain = [new Date(start_date_input), new Date(end_date_input)];
        xCScale.domain(newDomain);

        const dateRangeInDays = d3.timeDay.count(xCScale.domain()[0], xCScale.domain()[1]);
        let tickInterval;
        if (dateRangeInDays > 365 * 5) {
            tickInterval = d3.timeYear.every(1);
        } else if (dateRangeInDays > 365 * 2) { 
            tickInterval = d3.timeMonth.every(6); 
        } else if (dateRangeInDays > 365) { 
            tickInterval = d3.timeMonth.every(2); 
        } else if (dateRangeInDays > 180) {
            tickInterval = d3.timeMonth.every(1);
        } else if (dateRangeInDays > 90) { 
            tickInterval = d3.timeWeek.every(2); 
        } else if (dateRangeInDays > 30) {
            tickInterval = d3.timeWeek.every(1);
        } else if (dateRangeInDays > 10) {
            tickInterval = d3.timeDay.every(2); 
        } else {
            tickInterval = d3.timeDay.every(1);
        }

        svgC.select(".x-axis")
            .attr("class", "x-axis")
            .attr("transform", `translate(0,${heightC})`)
            .style("font-size", "14px")
            .transition()
            .duration(animDuration)
            .call(d3.axisBottom(xCScale)
                .tickValues(xCScale.ticks(tickInterval))
                .tickFormat(d3.timeFormat("%b %Y")))
            .call(g => g.select(".domain").remove())
            .selectAll(".tick line")
                .style("stroke-opacity", 0)

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
                    .duration(animDuration)
                    .attr("x1", d => xCScale(d))
                    .attr("x2", d => xCScale(d)),
                exit => exit.remove()
            );

        svgC.selectAll(".tick text")
            .style("fill", "#777");

        svgC.selectAll(".line")
            .data(sumstat)
            .join(
                enter => enter.append("path")
                    .attr("class", "line")
                    .attr("fill", "none")
                    .attr("stroke", d => color(d[0]))
                    .attr("stroke-width", 1.5)
                    .attr("clip-path", "url(#clip)")
                    .attr("d", d => d3.line()
                        .x(d => xCScale(new Date(d.timestamp)))
                        .y(d => yCScale(+d.duration))
                        (d[1])),
                update => update.transition()
                    .duration(animDuration)
                    .attr("clip-path", "url(#clip)")
                    .attr("d", d => d3.line()
                        .x(d => xCScale(new Date(d.timestamp)))
                        .y(d => yCScale(+d.duration))
                        (d[1])),
                exit => exit.remove()
            );
    }

    function drawBrush() {
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
                .tickValues(xBScale.ticks(d3.timeMonth.every(2)))
                .tickFormat(d3.timeFormat("%b %Y")))
            .call(g => g.select(".domain").remove())
            .selectAll(".tick line")
                .style("stroke-opacity", 0);

        svgB.selectAll(".tick text")
            .style("fill", "#777");

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

        svgB.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", widthB)
            .attr("height", heightB)
            .attr("stroke", "#777")
            .attr("fill", "none");

        const brush = d3.brushX()
            .extent([[0, 0], [widthB, heightB]])
            .on("brush end", brushed);

        svgB.append('g')
            .attr('class', 'brush')
            .call(brush);

        function brushed({ selection }) {
            if (selection) {
                const [x0, x1] = selection.map(xBScale.invert);                    
                start_date_input = new Date(x0).toISOString().split('T')[0];
                end_date_input = new Date(x1).toISOString().split('T')[0];
                svgC.selectAll(".tooltip-circle").remove();
                updateChart();
            }
        }
    }

    let isModalVisible = $state(false);
    function showModal() {
        isModalVisible = true;
    };

    function hideModal() {
        if (event.target === event.currentTarget) {
            isModalVisible = false;
        }
    };
</script>

<div id="container">
    <div class="app">
        <div>
            <input id="app" type="text" bind:value={app} onfocusout={getData} />
            <span id="help-icon" onclick={showModal}>?</span>
        </div>
    </div>
    <div class="date-container">
        <span>Start Date: {start_date_input}</span>
        <span>End Date: {end_date_input}</span>
    </div>

    <svg id="brush"></svg>
    <div id="notice">{notice}</div>
    <svg id="chart"></svg>
    <div id="tooltip"></div>

    <!-- Modal Structure -->
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div id="modal" class="modal" class:visible={isModalVisible} onclick={hideModal}>
        <div class="modal-content">
            <span class="close" onclick={hideModal}>&times;</span>
            <h2>Available App Inputs</h2>
            {#if app_names.length > 0}
                <table class="modal-table">
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>App Title</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each app_names as item}
                            <tr>
                                <td>{item.app}</td>
                                <td>{item.title}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            {:else}
                <p>Loading...</p>
            {/if}
        </div>
    </div>
</div>


<style>
    .app {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 20px;
    }

    .app div {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60%;
    }
    .app input {
        width: 90%;
        flex: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 16px;
        outline: none;
        transition: border-color 0.3s;
    }

    .app input:focus {
        border-color: #535bf2;
        box-shadow: 0 0 4px rgba(0, 123, 255, 0.5);
    }

    .date-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        font-size: 1.2em;
        padding: 20px;
    }
    #notice {
        text-align: center;
        font-size: 0.8em;
        color: #777;
        margin-top: 10px;
        margin-bottom: -4px;
    }


    #help-icon {
        cursor: pointer;
        margin-left: 10px;
        font-weight: bold;
        color: #646cff;
        font-size: 1.4em;
    }

    #help-icon:hover {
        color: #535bf2;
    }

    .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        overflow: auto;
        padding-top: 60px;
    }

    .modal-content {
        background-color: #222222;
        margin: 2.5% auto 10%;
        padding: 20px;
        border: 1px solid #888;
        width: 60%;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .modal-content h2 {
        margin-top: 0;
        color: #fff;
        font-size: 1.4em;
        font-weight: bold;
        text-align: center;
    }

    .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
    }

    .close:hover,
    .close:focus {
        color: #7e7e7e;
        text-decoration: none;
        cursor: pointer;
    }

    .modal-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 5px;
        margin-top: 20px;
    }

    .modal-table th,
    .modal-table td {
        text-align: left;
        padding: 5px 7px;
        border: 1px solid #868686;
    }

    .modal-table th {
        background-color: #4e4e4e;
        font-weight: bold;
    }

    .modal-table tr:nth-child(even) {
        background-color: #303030;
    }

    .visible {
        display: block;
    }
</style>
