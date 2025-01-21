<script lang="ts">
    // @ts-nocheck
    import * as d3 from "d3";
    import { onMount } from "svelte";

	// Data setup
	onMount(() => {
	const data = [
		{ month: "Jan", HadesII: 13, Overwatch2: 35, Other: 10 },
		{ month: "Feb", HadesII: 16, Overwatch2: 60, Other: 10 },
		{ month: "Mar", HadesII: 40, Overwatch2: 32, Other: 30 },
		{ month: "Apr", HadesII: 25, Overwatch2: 15, Other: 60 },
		{ month: "May", HadesII: 55, Overwatch2: 41, Other: 4 },
	];

	const colors = {
		HadesII: "#007bff",
		Overwatch2: "#ff5733",
		Other: "#cccccc"
	};

	// SVG dimensions
	const margin = { top: 40, right: 20, bottom: 40, left: 50 };
	const width = 800 - margin.left - margin.right;
	const height = 400 - margin.top - margin.bottom;

	// Create SVG
	const svg = d3.select(".chart")
		.append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", `translate(${margin.left},${margin.top})`);

	// Tooltip setup
	const tooltip = d3.select(".tooltip");

	// Stack data
	const stackKeys = ["HadesII", "Overwatch2", "Other"];
	const stackedData = d3.stack()
		.keys(stackKeys)
		(data);

	// Scales
	const xScale = d3.scaleBand()
		.domain(data.map(d => d.month))
		.range([0, width])
		.padding(0.2);

	const yScale = d3.scaleLinear()
		.domain([0, d3.max(stackedData[stackedData.length - 1], d => d[1])])
		.nice()
		.range([height, 0]);

	const colorScale = d3.scaleOrdinal()
		.domain(stackKeys)
		.range([colors.HadesII, colors.Overwatch2, colors.Other]);

	// Axes
	svg.append("g")
		.attr("class", "x-axis")
		.attr("transform", `translate(0,${height})`)
		.call(d3.axisBottom(xScale));

	svg.append("g")
		.attr("class", "y-axis")
		.call(d3.axisLeft(yScale).ticks(5));

	// Bars
	svg.selectAll(".layer")
		.data(stackedData)
		.join("g")
		.attr("fill", d => colorScale(d.key))
		.selectAll("rect")
		.data(d => d)
		.join("rect")
		.attr("class", "bar")
		.attr("x", d => xScale(d.data.month))
		.attr("y", d => yScale(d[1]))
		.attr("height", d => yScale(d[0]) - yScale(d[1]))
		.attr("width", xScale.bandwidth())
		.on("mouseover", function (event, d) {
			const [start, end] = d;
			const appName = d3.select(this.parentNode).datum().key;
			const total = d.data.HadesII + d.data.Overwatch2 + d.data.Other;
			const percentage = ((end - start) / total * 100).toFixed(1);

			tooltip
				.style("opacity", 1)
				.html(`
					<strong>${d.data.month}</strong><br>
					${appName}: ${percentage}%<br>
					Total: ${end - start} hrs
				`)
				.style("left", `${event.pageX + 10}px`)
				.style("top", `${event.pageY - 20}px`);
		})
		.on("mousemove", function (event) {
			tooltip
				.style("left", `${event.pageX + 10}px`)
				.style("top", `${event.pageY - 20}px`);
		})
		.on("mouseout", function () {
			tooltip.style("opacity", 0);
		});
	});

</script>

<div>
	
    <div class="chart"></div>
    <div class="tooltip"></div>
    <script src="chart.js"></script>
</div>

<style>
	body {
		font-family: Arial, sans-serif;
	}
	.chart {
		margin: 50px auto;
		max-width: 800px;
	}
	.tooltip {
		position: absolute;
		background-color: rgb(95, 91, 91);
		border: 1px solid #ccc;
		border-radius: 5px;
		padding: 10px;
		font-size: 14px;
		pointer-events: none;
		opacity: 0;
		transition: opacity 0.2s;
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
	}
	.bar {
		stroke: #fff;
	}
</style>
