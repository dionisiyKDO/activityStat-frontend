<!-- routes/+page.svelte -->
<script>
	
</script>

<div class="w-auto flex justify-center text-9xl">
	Aboba
</div>










<!-- 
<script>
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	let chartContainer;

	onMount(() => {
		const margin = { top: 20, right: 30, bottom: 50, left: 50 };
		const width = 800 - margin.left - margin.right;
		const height = 400 - margin.top - margin.bottom;

		// Generate a larger dataset
		const data = d3.range(0, 100).map((i) => ({
			date: new Date(2023, 0, 1 + i), // Incrementing dates
			value: Math.sin(i / 10) * 20 + i + Math.random() * 10 // Sine wave with noise
		}));

		const svg = d3
			.select(chartContainer)
			.append('svg')
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom);

		const chartArea = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);

		const xScale = d3
			.scaleTime()
			.domain(d3.extent(data, (d) => d.date))
			.range([0, width]);

		const yScale = d3
			.scaleLinear()
			.domain([0, d3.max(data, (d) => d.value) + 10])
			.range([height, 0]);

		const xAxis = d3.axisBottom(xScale).ticks(10);
		const yAxis = d3.axisLeft(yScale);

		const line = d3
			.line()
			.x((d) => xScale(d.date))
			.y((d) => yScale(d.value));

		// Add gridlines
		function addGridlines() {
			chartArea
				.append('g')
				.attr('class', 'grid x-grid')
				.attr('transform', `translate(0, ${height})`)
				.call(d3.axisBottom(xScale).ticks(10).tickSize(-height).tickFormat(''));

			chartArea
				.append('g')
				.attr('class', 'grid y-grid')
				.call(d3.axisLeft(yScale).ticks(10).tickSize(-width).tickFormat(''));
		}

		addGridlines();

		// Append line path
		const linePath = chartArea
			.append('path')
			.datum(data)
			.attr('fill', 'none')
			.attr('stroke', 'steelblue')
			.attr('stroke-width', 2)
			.attr('d', line);

		// Add x and y axes
		const xAxisGroup = chartArea
			.append('g')
			.attr('class', 'x-axis')
			.attr('transform', `translate(0, ${height})`)
			.call(xAxis);

		const yAxisGroup = chartArea.append('g').attr('class', 'y-axis').call(yAxis);

		// Brush feature
		const brush = d3
			.brushX()
			.extent([
				[0, 0],
				[width, height]
			])
			.on('end', brushed);

		const brushGroup = chartArea.append('g').attr('class', 'brush').call(brush);

		function brushed({ selection }) {
			if (!selection) return;

			const [x0, x1] = selection.map(xScale.invert);
			xScale.domain([x0, x1]);

			// Update x-axis
			xAxisGroup.call(xAxis);

			// Update line path
			linePath.attr('d', line);

			// Clear brush after zoom
			brushGroup.call(brush.move, null);
		}

		// Double-click to reset zoom
		svg.on('dblclick', () => {
			xScale.domain(d3.extent(data, (d) => d.date));
			xAxisGroup.call(xAxis);
			linePath.attr('d', line);
		});

		// Update the brush to use the currently zoomed xScale
		function updateBrush() {
			brush.extent([
				[0, 0],
				[width, height]
			]);
			brushGroup.call(brush);
		}

		// Re-apply brush whenever xScale is updated
		svg.on('dblclick', () => {
			xScale.domain(d3.extent(data, (d) => d.date));
			xAxisGroup.call(xAxis);
			linePath.attr('d', line);
			updateBrush(); // Update brush extent after reset
		});
	});
</script>

<div bind:this={chartContainer} class="chart-container"></div>

<style>
	.chart-container {
		display: flex;
		justify-content: center;
		align-items: center;
	}

	svg {
		font-family: sans-serif;
		font-size: 12px;
	}

	.grid .tick line {
		stroke: #e0e0e0;
	}

	.brush .selection {
		fill: #69b3a2;
		fill-opacity: 0.3;
		stroke: #69b3a2;
		shape-rendering: crispEdges;
	}
</style> 
-->
