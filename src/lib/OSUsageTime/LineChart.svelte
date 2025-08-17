<script lang="ts">
	// @ts-ignore: Ignore TS errors for d3 library
	import * as d3 from 'd3';
	import { type OSUsageData, type margin } from '$lib/types';

	// #region Data Preparation
	let chartContainer: HTMLDivElement;
	let chartSvg: SVGSVGElement;
	let brushSvg: SVGSVGElement;
	let tooltipDiv: HTMLDivElement;

	interface Props {
		data: OSUsageData[] | null;
	}
	let { data }: Props = $props();

	// Date range calculation
	const dateExtent = d3.extent(data, (d: any) => d.date) as [Date, Date];
	const initialStartDate = dateExtent[0].toISOString().split('T')[0];
	const initialEndDate = dateExtent[1].toISOString().split('T')[0];

	let currentStartDate = $state(initialStartDate);
	let currentEndDate = $state(initialEndDate);

	let filteredData = $derived(
		data?.filter((d: any) => {
			return d.date >= new Date(initialStartDate) && d.date <= new Date(initialEndDate);
		})
	);

	$inspect('Filtered Data', filteredData);

	const colorScale = d3
		.scaleOrdinal<string>()
		.range([
			// 4 distinct colors
			'#ff6384', // Red
			'#2196f3', // Light Blue

			'#ffce56', // Yellow
			'#4caf50', // Green
		]);

	let animDuration = 0; // better keep it zero for performance
	// #endregion

	$effect(() => {
		drawChart();
	});

	$effect(() => {
		if (!chartContainer) return;

		const resizeObserver = new ResizeObserver(() => {
			if (data) {
				drawChart();
			}
		});

		resizeObserver.observe(chartContainer);
		return () => resizeObserver.disconnect();
	});

	function drawChart() {
		//#region Draw Main Chart
		if (!chartContainer || !chartSvg || !data?.length) return;

		// Clear previous chart
		d3.select(chartSvg).selectAll('*').remove();

		// Get actual container dimensions
		const containerRect = chartContainer.getBoundingClientRect();
		const margin: margin = { top: 10, right: 30, bottom: 30, left: 60 };
		const width = containerRect.width - margin.left - margin.right;
		const chartHeight = 350;
		const height = chartHeight - margin.top - margin.bottom;

		if (width <= 0 || height <= 0) return;

		// Draw the "brush" chart
		drawBrush();

		// SVG Initialization
		const svg = d3
			.select(chartSvg)
			.attr('width', containerRect.width)
			.attr('height', chartHeight)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Create a clipping path to constrain line visibility when zooming
		svg
			.append('defs')
			.append('clipPath')
			.attr('id', 'clip')
			.append('rect')
			.attr('width', width)
			.attr('height', height);

		// Define Time scale (x-axis)
		let xScale = d3
			.scaleTime()
			.domain(d3.extent(filteredData, (d: any) => d.date))
			.range([0, width]);

		// Define Linear scale (y-axis)
		let yScale = d3
			.scaleLinear()
			.domain([0, d3.max(data, (d: any) => d.duration)])
			.range([height, 0])
			.nice();

		// #region Axes, Grid, Bounds
		// Draw the x-axis
		const dateRange = xScale.domain();
		const daySpan = d3.timeDay.count(dateRange[0], dateRange[1]);

		let tickInterval: d3.TimeInterval;
		let tickFormat: (date: Date) => string;

		if (daySpan > 365 * 2) {
			tickInterval = d3.timeMonth.every(6) || d3.timeMonth;
			tickFormat = d3.timeFormat('%Y');
		} else if (daySpan > 365) {
			tickInterval = d3.timeMonth.every(2) || d3.timeMonth;
			tickFormat = d3.timeFormat("%b '%y");
		} else if (daySpan > 90) {
			tickInterval = d3.timeMonth.every(1) || d3.timeMonth;
			tickFormat = d3.timeFormat('%b %Y');
		} else {
			tickInterval = d3.timeWeek.every(2) || d3.timeWeek;
			tickFormat = d3.timeFormat('%m/%d/%y');
		}

		const xAxis = svg
			.append('g')
			.attr('class', 'x-axis')
			.attr('transform', `translate(0,${height})`)
			.style('font-size', '14px')
			.call(d3.axisBottom(xScale).ticks(tickInterval).tickFormat(tickFormat))
			// .call(d3.axisBottom(xScale).ticks(d3.timeMonth.every(3)).tickFormat(d3.timeFormat('%b %Y')))
			.call((g: any) => {
				g.select('.domain').remove();
				g.selectAll('.tick line').style('stroke-opacity', 0);
				g.selectAll('.tick text').style('fill', '#777');
			});

		// Draw the y-axis
		const yAxis = svg
			.append('g')
			.attr('class', 'y-axis')
			.style('font-size', '14px')
			.call(d3.axisLeft(yScale))
			.call((g: any) => {
				g.select('.domain').remove();
				g.selectAll('.tick line').style('stroke-opacity', 0);
				g.selectAll('.tick text').style('fill', '#777');
			});

		// Draw grid lines
		svg
			.selectAll('.x-grid')
			.data(xScale.ticks(d3.timeMonth.every(1) || d3.timeMonth))
			.join('line')
			.attr('class', 'x-grid')
			.attr('x1', (d: any) => xScale(d))
			.attr('x2', (d: any) => xScale(d))
			.attr('y1', 0)
			.attr('y2', height)
			.attr('stroke', '#e0e0e0')
			.attr('stroke-width', 0.5)
			.attr('stroke-opacity', 0.33);

		svg
			.selectAll('.y-grid')
			.data(yScale.ticks())
			.join('line')
			.attr('x1', 0)
			.attr('x2', width)
			.attr('y1', (d: any) => yScale(d))
			.attr('y2', (d: any) => yScale(d))
			.attr('stroke', '#e0e0e0')
			.attr('stroke-width', 0.5)
			.attr('stroke-opacity', 0.33);

		// Add y-axis label
		svg
			.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', -margin.left)
			.attr('x', -height / 2)
			.attr('dy', '1em')
			.style('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('fill', '#777')
			.text('Duration (Hours)');

		// Draw chart boundary
		svg
			.append('rect')
			.attr('x', 0)
			.attr('y', 0)
			.attr('width', width)
			.attr('height', height)
			.attr('stroke', '#777')
			.attr('stroke-width', 1)
			.attr('fill', 'none');
		// #endregion

		// #region Chart Lines
		// Draw the lines for each 'app' in the dataset
		const line = d3
			.line<OSUsageData>()
			.x((d: any) => xScale(d.date))
			.y((d: any) => yScale(d.duration))
			.curve(d3.curveLinear);
		

		const OSGroups = d3.group(filteredData, (d: any) => d.platform);

		// Draw the lines for each 'app' in the dataset.
		svg
			.selectAll('.os-line')
			.data(OSGroups)
			.join('path')
			.attr('class', 'line')
			.attr('fill', 'none')
			.attr('stroke', (d: any) => colorScale(d[0]))
			.attr('stroke-width', 1.5)
			.attr('clip-path', 'url(#clip)')
			.attr('d', (d: any) => line(d[1]));

		// #endregion

		// #region Tooltip
		// Set up the tooltip line to indicate the cursor's x-position
		const tooltipLine = svg
			.append('line')
			.attr('stroke', '#fff')
			.attr('stroke-width', 1)
			.attr('opacity', 0);

		// Set up the tooltip container
		const tooltip = d3
			.select(tooltipDiv)
			.style('opacity', 0)
			.style('position', 'fixed')
			.style('white-space', 'nowrap')
			.style('z-index', '1000')
			.style('pointer-events', 'none')
			.style('background-color', '#1a1a1a')
			.style('border', 'solid 1px #646cff')
			.style('color', 'rgba(255, 255, 255, 0.87)')
			.style('padding', '7px')
			.style('border-radius', '2px')
			.style('box-shadow', '0 0 10px rgba(0, 0, 0, 0.1)')
			.style('font-size', '12px');

		// Add an invisible rectangle to listen for mouse events
		const listeningRect = svg
			.append('rect')
			.attr('width', width)
			.attr('height', height)
			.attr('opacity', 0)
			.on('mousemove', drawTooltip)
			.on('mouseout', removeTooltip);

		// Handles tooltip rendering and positioning on mousemove
		function drawTooltip(event: any) {
			const [mouseXsvg, mouseYsvg] = d3.pointer(event);
			const mouseX = event.clientX;
			const mouseY = event.clientY;

			// Find the closest data points for each app
			const points = Array.from(OSGroups, ([key, values]) => {
				const closest = d3.least(values, (d: any) => Math.abs(xScale(d.date) - mouseXsvg));
				if (!closest) return null; // Handle empty data

				return {
					platform: key,
					date: closest.date,
					duration: closest.duration,
					x: xScale(closest.date),
					y: yScale(closest.duration),
					color: colorScale(key)
				};
			}).filter(Boolean); // Remove nulls
			if (points.length === 0) return; // additional check

			// Tooltip positioning
			const tooltipWidth = tooltip.node()?.offsetWidth + 20 || 0; // 20 for browser scrollbar width
			const tooltipHeight = tooltip.node()?.offsetHeight || 0;
			let tooltipLeft = mouseX + 20;
			let tooltipTop = mouseY - 40;

			// Ensure the tooltip stays within viewport bounds
			if (tooltipLeft + tooltipWidth > window.innerWidth) tooltipLeft = mouseX - tooltipWidth - 10;
			if (tooltipTop + tooltipHeight > window.innerHeight) tooltipTop = mouseY - tooltipHeight - 10;

			// Show the tooltip
			tooltip.style('left', `${tooltipLeft}px`).style('top', `${tooltipTop}px`).style('opacity', 1);

			// Build tooltip content
			const maxDuration = Math.max(...points.map((p: any) => p.duration));
			const tooltipContent = `
                <div><strong>Date:</strong> ${d3.timeFormat('%b %d, %Y')(points[0]?.date)}</div>
                <hr> 
				${points
					.map(
						(p: any) => `
					<div>
                        <strong style="color:${p.color}"> ${p.platform} </strong> <br>
                        Duration: ${
													p?.duration === maxDuration
														? `<strong style="color: white">${p.duration} Hours</strong>` // if it's the max duration, highlight it
														: `${p.duration} Hours`
												}
                    </div>`
					)
					.join('')}`;
			tooltip.html(tooltipContent);

			// Update the tooltip line position
			tooltipLine
				.attr('x1', mouseXsvg)
				.attr('x2', mouseXsvg)
				.attr('y1', 0)
				.attr('y2', height)
				.attr('stroke-width', 1)
				.attr('opacity', 0.2);

			// Add or update circles at the data points
			const circles = svg.selectAll('.tooltip-circle').data(points, (d: any) => d.app);
			circles.exit().remove(); // Remove unneeded circles

			circles
				.attr('cx', (d: any) => d.x)
				.attr('cy', (d: any) => d.y)
				.attr('r', 4)
				.attr('fill', (d: any) => d.color)
				.style('pointer-events', 'none');

			circles
				.enter()
				.append('circle')
				.attr('class', 'tooltip-circle')
				.attr('cx', (d: any) => d.x)
				.attr('cy', (d: any) => d.y)
				.attr('r', 4)
				.attr('fill', (d: any) => d.color)
				.style('pointer-events', 'none');
		}

		// Removes the tooltip and related elements on mouseout
		function removeTooltip() {
			tooltip.style('opacity', 0); // Hide tooltip
			tooltipLine.attr('opacity', 0); // Hide tooltip line
			svg.selectAll('.tooltip-circle').remove(); // Remove circles
		}
		// #endregion

		// #region Update Function
		// Function to update chart on brush selection
		function updateChart(start: Date, end: Date) {
			const newDomain: [Date, Date] = [new Date(start), new Date(end)];
			xScale.domain(newDomain);

			// Calculate date range in different units for more precise tick handling
			const dateRangeInDays = d3.timeDay.count(xScale.domain()[0], xScale.domain()[1]);
			const dateRangeInHours = dateRangeInDays * 24;
			const width = xScale.range()[1] - xScale.range()[0];

			// Target roughly one tick per 100 pixels for optimal readability
			const targetTickCount = Math.max(2, Math.floor(width / 100));

			// Determine optimal tick interval and format
			let gridInterval;
			let tickInterval;
			let tickFormat;

			if (dateRangeInDays > 365 * 2) {
				// 2-5 years
				gridInterval = d3.timeMonth.every(1);
				tickInterval = d3.timeMonth.every(6) || d3.timeMonth;
				tickFormat = d3.timeFormat('%Y');
			} else if (dateRangeInDays > 365) {
				// 1-2 years
				gridInterval = d3.timeMonth.every(1);
				tickInterval = d3.timeMonth.every(2) || d3.timeMonth;
				tickFormat = d3.timeFormat('%b %Y');
			} else if (dateRangeInDays > 180) {
				// 6 months - 1 year
				gridInterval = d3.timeWeek.every(2);
				tickInterval = d3.timeMonth.every(1) || d3.timeMonth;
				tickFormat = d3.timeFormat('%b %Y');
			} else if (dateRangeInDays > 90) {
				// 3-6 months
				gridInterval = d3.timeWeek.every(1);
				tickInterval = d3.timeMonth.every(1) || d3.timeMonth;
				tickFormat = d3.timeFormat('%b %Y');
			} else if (dateRangeInDays > 30) {
				// 1-3 months
				gridInterval = d3.timeWeek.every(1);
				tickInterval = d3.timeWeek.every(2) || d3.timeWeek;
				tickFormat = d3.timeFormat('%m/%d/%y');
			} else if (dateRangeInDays > 7) {
				// 1-4 weeks
				gridInterval = d3.timeDay.every(Math.ceil(dateRangeInDays / targetTickCount));
				tickInterval = d3.timeWeek.every(2) || d3.timeWeek;
				tickFormat = d3.timeFormat('%m/%d/%y');
			} else {
				// 1-7 days
				gridInterval = d3.timeDay.every(1);
				tickInterval = d3.timeDay.every(1);
				tickFormat = d3.timeFormat('%a %m/%d/%y');
			}

			// Update the x-axis with new ticks
			const xAxis = svg
				.select('.x-axis')
				.call(d3.axisBottom(xScale).ticks(tickInterval).tickFormat(tickFormat))
				.call((g: any) => {
					g.select('.domain').remove();
					g.selectAll('.tick line').style('stroke-opacity', 0);
				});

			// Update x-grid lines with the same tick interval
			svg
				.selectAll('.x-grid')
				.data(xScale.ticks(gridInterval))
				.join(
					(enter: any) =>
						enter
							.append('line')
							.attr('class', 'x-grid')
							.attr('y1', 0)
							.attr('y2', height)
							.attr('stroke', '#e0e0e0')
							.attr('stroke-width', 0.5)
							.attr('stroke-opacity', 0.33)
							.attr('x1', (d: any) => xScale(d))
							.attr('x2', (d: any) => xScale(d)),
					(update: any) =>
						update
							.transition()
							.duration(animDuration)
							.attr('x1', (d: any) => xScale(d))
							.attr('x2', (d: any) => xScale(d)),
					(exit: any) => exit.remove()
				);

			// Style tick text
			svg.selectAll('.tick text').style('fill', '#777');

			// Update line paths
			svg
				.selectAll('.line')
				.data(OSGroups)
				.join('path')
				.attr('class', 'line')
				.attr('fill', 'none')
				.attr('stroke', (d: any) => colorScale(d[0]))
				.attr('stroke-width', 1.5)
				.attr('clip-path', 'url(#clip)')
				.attr('d', (d: any) => line(d[1]));
		}
		// #endregion

		function drawBrush() {
			// #region Brush Chart
			// Brush chart to zoom and pan chart
			if (!brushSvg) return;

			d3.select(brushSvg).selectAll('*').remove();

			const containerRect = chartContainer.getBoundingClientRect();
			const margin: margin = { top: 0, right: 30, bottom: 25, left: 60 };
			const width = containerRect.width - margin.left - margin.right;
			const brushHeight = 60;
			const height = brushHeight - margin.top - margin.bottom;

			// SVG element for brush chart
			const svg = d3
				.select(brushSvg)
				.attr('width', containerRect.width)
				.attr('height', brushHeight)
				.append('g')
				.attr('transform', `translate(${margin.left},${margin.top})`);

			// regular x-scale for chart
			let xScale = d3.scaleTime().domain(dateExtent).range([0, width]);

			// const for calculating
			const constXScale = d3.scaleTime().domain(dateExtent).range([0, width]);

			// y-scale needed for lines
			let yScale = d3
				.scaleLinear()
				.domain([0, d3.max(data, (d: any) => d.duration) || 0])
				.range([height, 0])
				.nice();

			// #region Brush Axes, Grid, Bounds
			// x-axis
			let xAxis = svg
				.append('g')
				.attr('transform', `translate(0,${height})`)
				.style('font-size', '14px')
				.call(
					d3
						.axisBottom(xScale)
						.tickValues(xScale.ticks(d3.timeMonth.every(4)))
						.tickFormat(d3.timeFormat('%b %Y'))
				)
				.call((g: any) => g.select('.domain').remove())
				.selectAll('.tick line')
				.style('stroke-opacity', 0);

			svg.selectAll('.tick text').style('fill', '#777');

			// Draw grid lines
			svg
				.selectAll('.x-grid')
				.data(xScale.ticks(20))
				.join('line')
				.attr('class', 'x-grid')
				.attr('x1', (d: any) => xScale(d))
				.attr('x2', (d: any) => xScale(d))
				.attr('y1', 0)
				.attr('y2', height)
				.attr('stroke', '#e0e0e0')
				.attr('stroke-width', 0.5)
				.attr('stroke-opacity', 0.33);

			// Add border around brush chart
			svg
				.append('rect')
				.attr('x', 0)
				.attr('y', 0)
				.attr('width', width)
				.attr('height', height)
				.attr('stroke', '#777')
				.attr('fill', 'none');

			// #endregion

			// #region Brush Chart Lines
			// Group data by 'app' for line chart
			const OSGroups = d3.group(filteredData, (d: any) => d.platform);

			const line = d3
				.line<OSUsageData>()
				.x((d: any) => xScale(d.date))
				.y((d: any) => yScale(d.duration));

			svg
				.selectAll('.line')
				.data(OSGroups)
				.join('path')
				.attr('class', 'line')
				.attr('fill', 'none')
				.attr('stroke', (d: any) => colorScale(d[0]))
				.attr('stroke-width', 1.5)
				.attr('d', (d: any) => line(d[1]));

			// #endregion

			// #region Brush functionality
			const brush = d3
				.brushX()
				.extent([
					[0, 0],
					[width, height]
				])
				.on('brush end', brushed);

			const brushGroup = svg.append('g').attr('class', 'brush').call(brush);

			// Brush Event Handlers
			function brushed({ selection }: { selection: [number, number] | null }) {
				if (!selection) return;

				// Invert selection to date range
				const x0 = constXScale.invert(selection[0]);
				const x1 = constXScale.invert(selection[1]);

				currentStartDate = x0.toISOString().split('T')[0];
				currentEndDate = x1.toISOString().split('T')[0];

				// Update main chart with the selected range
				updateChart(x0, x1);
			}

			// Reset chart on double-click
			svg.on('dblclick', () => {
				currentStartDate = new Date(dateExtent[0]).toISOString().split('T')[0];
				currentEndDate = new Date(dateExtent[1]).toISOString().split('T')[0];

				updateChart(dateExtent[0], dateExtent[1]);

				// Clear brush selection
				brushGroup.call(brush.move, null);
			});
			// #endregion

			// #endregion
		}
	}
</script>

<div bind:this={chartContainer}>
	<div class="my-2 flex justify-center gap-4" style="color: #777;">
		<span>Start Date: {currentStartDate}</span>
		<span>End Date: {currentEndDate}</span>
	</div>
	<svg bind:this={brushSvg}></svg>
	<svg bind:this={chartSvg}></svg>
	<div bind:this={tooltipDiv}></div>
</div>

<style>
</style>
