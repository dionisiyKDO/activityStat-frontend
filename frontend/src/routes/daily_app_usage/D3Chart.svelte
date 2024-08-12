<script>
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

	let data = $state([]);
    let waiting = $state('Loading...');


    let app = $state("c");
    let startDate = $state('2020-01-01');
    let endDate = $state('2024-08-11');
    let filteredData = $derived(
        data.filter(d => {
            const date = new Date(d.timestamp);
            d.date = date.toISOString().split('T')[0]; // create date string
            return date >= new Date(startDate) && date <= new Date(endDate);
        })
    );


    // let chart = $derived(drawChart());

    async function fetchData() {
        const response = await fetch("/api/daily_app_usage/chrome.exe");
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

    function update() {
        // console.log('filteredData length: ', filteredData.length);
        // console.log('Data: ', filteredData);
        console.log('d.length * 10', filteredData.length * 10);
        
        
        drawChart();
    }

    function drawChart() {
        // set the dimensions and margins of the graph
        const container = d3.select("#container");
        const margin = {top: 10, right: 30, bottom: 30, left: 60},
            width = container.node().getBoundingClientRect().width - margin.left - margin.right,
            height = 400 - margin.top - margin.bottom;

        // append the svg object to the body of the page
        d3.select("#chart").selectAll("*").remove();
        const svg = d3.select("#chart")
            .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
            // .attr("width", width + margin.left + margin.right)
            // .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);


        // group the data: I want to draw one line per group
        const sumstat = d3.group(filteredData, d => d.app); // nest function allows to group the calculation per level of a factor
        
        // Add X axis --> it is a date format
        // const x = d3.scaleLinear()
        //     .domain(d3.extent(filteredData, function(d) { return d.timestamp; }))
        //     .range([ 0, width ]);
        const x = d3.scaleBand()
            .domain(filteredData.map(d => d.date))
            .range([ 0, width ])
            .padding(0.1);
        svg.append("g")
            .attr("transform", `translate(0, ${height})`)
            .call(d3.axisBottom(x).tickValues(x.domain().filter(function(d,i){ return !(i % Math.round(filteredData.length * 0.07)  )}))); // decrease interval of ticks (labels on x-axis), 0.0..1 - the less number, the more labels. (i % Math.round(filteredData.length * 0.07) keeps so number of labels on x-axis is somewhat constant depending on the amount of data)

        // Add Y axis
        const y = d3.scaleLinear()
            .domain([0, d3.max(filteredData, function(d) { return +d.duration; })])
            .range([ height, 0 ])
            .nice();
        svg.append("g")
            .call(d3.axisLeft(y));

        // color palette
        const color = d3.scaleOrdinal()
            .range(['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999'])

        // Draw the line
        svg.selectAll(".line")
            .data(sumstat)
            .join("path")
                .attr("fill", "none")
                .attr("stroke", function(d){ return color(d[0]) })
                .attr("stroke-width", 1.5)
                .attr("d", function(d){
                    return d3.line()
                        .x(function(d) { return x(d.date); })
                        .y(function(d) { return y(+d.duration); })
                        (d[1])
                    })

    }
</script>

<div id="container">
    <input id="app" type="text" bind:value={app} />
    <input type="date" id="start" bind:value={startDate} />
    <input type="date" id="end" bind:value={endDate} />

    <button onclick={update}>Update</button>
    <svg id="chart" width="800" height="400"></svg>
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
