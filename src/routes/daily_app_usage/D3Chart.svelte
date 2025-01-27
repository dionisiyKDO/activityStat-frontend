<script lang="ts">
	// @ts-ignore: Ignore TS errors for d3 library
	import * as d3 from 'd3';
	import { onMount } from 'svelte';
	import { type AppUsageData, type margin } from './load';

	// #region Data Preparation
	let { data }: { data: AppUsageData[] | null } = $props();
	let filteredData = $derived(
		data?.filter((d: any) => {
			return d.date >= new Date(start_date) && d.date <= new Date(end_date);
		})
	);

	// d3.extent(data, (d: any) => d.date) 	- ['1999-01-01T00:00:00.000Z', '2050-01-01T00:00:00.000Z']
	// .toISOString().split('T') 			- ['1999-01-01', '0:00:00.000Z']
	const start_date = d3.extent(data, (d: any) => d.date)[0].toISOString().split('T')[0];
	const end_date = d3.extent(data, (d: any) => d.date)[1].toISOString().split('T')[0];
	
	let start_date_label = $state(d3.extent(data, (d: any) => d.date)[0].toISOString().split('T')[0]);
	let end_date_label = $state(d3.extent(data, (d: any) => d.date)[1].toISOString().split('T')[0]);

	let animDuration = 0; // better keep it zero for performance
	// #endregion
	
	$effect(() => {
		drawChart();
	});

	// TODO: tooltip out of bounds fix
	function drawChart() {
		// #region Main chart
		d3.select('#chart').selectAll('*').remove();

		// Chart container dimensions and margins
		const container = d3.select('#container');
		const margin: margin = { top: 10, right: 30, bottom: 30, left: 60 };
		const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
		const height = 400 - margin.top - margin.bottom;

		// Draw the "brush" chart
		drawBrush();

		// #region SVG Initialization
		let svg = d3
			.select('#chart')
			.attr(
				'viewBox',
				`0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`
			)
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

		// Group data by 'app' (to separate lines per app).
		const sumstat = d3.group(filteredData, (d: any) => d.app);
		// Define a color scale for apps
		const color = d3
			.scaleOrdinal()
			.range([
				'#e41a1c',
				'#377eb8',
				'#4daf4a',
				'#984ea3',
				'#ff7f00',
				'#ffff33',
				'#a65628',
				'#f781bf',
				'#999999'
			]);

		// Define Time scale (x-axis)
		let xScale = d3
			.scaleTime()
			.range([0, width])
			.domain(d3.extent(filteredData, (d: any) => d.date));

		// Define Linear scale (y-axis)
		let yScale = d3
			.scaleLinear()
			.range([height, 0])
			.domain([0, d3.max(data, (d: any) => d.duration)])
			.nice();

		// #endregion

		// #region Axes, Grid, Bounds

		// Draw the x-axis
		let xAxis = svg
			.append('g')
			.attr('class', 'x-axis')
			.attr('transform', `translate(0,${height})`)
			.style('font-size', '14px')
			.call(
				d3.axisBottom(xScale)
					.ticks(10) // better? // TODO: play with ticks
					// .tickValues(xScale.ticks(d3.timeMonth.every(2)))  // old way to manage ticks
					.tickFormat(d3.timeFormat('%b %Y'))  // Custom tick format: "Jan 2023"
			)
			.call((g: any) => g.select('.domain').remove())
			.selectAll('.tick line')
			.style('stroke-opacity', 0);

		// Draw the y-axis
		let yAxis = svg
			.append('g')
			.attr('class', 'y-axis')
			.style('font-size', '14px')
			.call(d3.axisLeft(yScale))
			.call((g: any) => g.select('.domain').remove())
			.selectAll('.tick line')
			.style('stroke-opacity', 0);

		// Style tick text
		svg.selectAll('.tick text').style('fill', '#777');

		// Draw x-grid lines.
		const xGrid = svg
			.selectAll('xGrid')
			.data(xScale.ticks().slice(1, -1)) // Remove the first and last tick to prevent overlap
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

		// Draw y-grid lines.
		const yGrid = svg
			.selectAll('yGrid')
			.data(yScale.ticks())
			.join('line')
			.attr('x1', 0)
			.attr('x2', width)
			.attr('y1', (d: any) => yScale(d))
			.attr('y2', (d: any) => yScale(d))
			.attr('stroke', '#e0e0e0')
			.attr('stroke-width', 0.5)
			.attr('stroke-opacity', 0.33);

		// Add y-axis label.
		svg
			.append('text')
			.attr('transform', 'rotate(-90)')
			.attr('y', 0 - margin.left)
			.attr('x', 0 - height / 2)
			.attr('dy', '1em')
			.style('text-anchor', 'middle')
			.style('font-size', '14px')
			.style('fill', '#777')
			.style('font-family', 'sans-serif')
			.text('Duration');

		// Draw chart boundary.
		svg
			.append('rect')
			.attr('x', 0)
			.attr('y', 0)
			.attr('width', width)
			.attr('height', height)
			.attr('stroke', '#777')
			.attr('fill', 'none');

		// #endregion

		// #region Draw Chart Lines

		// Draw the lines for each 'app' in the dataset.
		svg
			.selectAll('.line')
			.data(sumstat, (d: any) => d[0]) // Key: app name
			.join(
				(enter: any) =>
					enter
						.append('path')
						.attr('class', 'line')
						.attr('fill', 'none')
						.attr('stroke', (d: any) => color(d[0]))
						.attr('stroke-width', 1.5)
						.attr('clip-path', 'url(#clip)')
						.attr('d', (d: any) =>
							d3
								.line()
								.x((d: any) => xScale(new Date(d.timestamp)))
								.y((d: any) => yScale(+d.duration))(d[1])
						),
				(update: any) =>
					update
						.transition()
						.duration(animDuration)
						.attr('clip-path', 'url(#clip)')
						.attr('d', (d: any) =>
							d3
								.line()
								.x((d: any) => xScale(new Date(d.timestamp)))
								.y((d: any) => yScale(+d.duration))(d[1])
						),
				(exit: any) => exit.remove()
			);

		// #endregion

		// #region Draw Tooltip

		// Set up the tooltip line to indicate the cursor's x-position
		const tooltipLine = svg
			.append('line')
			.attr('stroke', '#fff')
			.attr('stroke-width', 1)
			.attr('opacity', 0);
			
		// Set up the tooltip container
		const tooltip = d3
			.select('#tooltip')
			.style('opacity', 0)
			.style('position', 'absolute')
			.style('z-index', '10')
			.style('pointer-events', 'none')
			.style('background-color', '#1a1a1a')
			.style('border', 'solid 1px #646cff')
			.style('color', 'rgba(255, 255, 255, 0.87)')
			.style('padding', '5px')
			.style('border-radius', '2px')
			.style('box-shadow', '0 0 10px rgba(0, 0, 0, 0.1)');

		// Add an invisible rectangle to listen for mouse events
		const listeningRect = svg
			.append('rect')
			.attr('width', width)
			.attr('height', height)
			.attr('opacity', 0)
			.on('mousemove', drawTooltip)
			.on('mouseout', removeTooltip);

		// Handles tooltip rendering and positioning on mousemove.
		function drawTooltip(event: any) {
			const [mouseXsvg, mouseYsvg] = d3.pointer(event);
			const mouseX = event.clientX;
			const mouseY = event.clientY;

			// Find the closest data points for each app
			const points = Array.from(sumstat, ([key, values]) => {
				const closest = d3.least(values, (d: any) => Math.abs(xScale(d.date) - mouseXsvg));
				if (!closest) return null; // Handle empty data
				return {
					app: key,
					date: closest.date,
					duration: closest.duration,
					x: xScale(closest.date),
					y: yScale(closest.duration),
					color: color(key)
				};
			}).filter(Boolean); // Remove nulls
			if (points.length === 0) return; // additional check

			// Tooltip positioning
			const tooltipWidth = tooltip.node()?.offsetWidth || 0;
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
				${points.map((p: any) => `
					<div>
                        <strong style="color:${p.color}"> ${p.app} </strong> <br>
                        Duration: ${p?.duration === maxDuration
							? `<strong style="color: white">${p.duration} Hours</strong>` // if it's the max duration, highlight it
							: `${p.duration} Hours`}
                    </div>`).join('')}`;
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
			const circles = svg.selectAll('.tooltip-circle').data(points, ((d: any) => d.app));
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

		// Removes the tooltip and related elements on mouseout.
		function removeTooltip() {
			tooltip.style('opacity', 0); // Hide tooltip
			tooltipLine.attr('opacity', 0); // Hide tooltip line
			svg.selectAll('.tooltip-circle').remove(); // Remove circles
		}
		
		
		// #endregion

		// #region Update chart on brush selection

		/**
		 * Updates the chart when the brush selection changes.
		 * @param start - Start date of the new domain.
		 * @param end - End date of the new domain.
		 */
		function updateChart(start: string, end: string) {
			const newDomain: [Date, Date] = [new Date(start), new Date(end)];
			xScale.domain(newDomain);

			// Calculate an appropriate tick interval based on the date range
			// TODO: play with tick intervals
			const dateRangeInDays = d3.timeDay.count(xScale.domain()[0], xScale.domain()[1]);
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

  			// Update the x-axis with new ticks
			svg
				.select('.x-axis')
				.call(d3.axisBottom(xScale)
						.tickValues(xScale.ticks(tickInterval))
						.tickFormat(d3.timeFormat('%b %Y'))
				)
				.call((g: any) => g.select('.domain').remove())
				.selectAll('.tick line')
				.style('stroke-opacity', 0);
			
  			// Update x-grid lines
			svg
				.selectAll('.x-grid')
				.data(xScale.ticks())
				.join(
					(enter: any) =>
						enter
							.append('line')
							.attr('class', 'x-grid')
							.attr('y1', 0)
							.attr('y2', height)
							.attr('stroke', '#e0e0e0')
							.attr('stroke-width', 0.5)
							.attr('stroke-opacity', 0.33),
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
				.data(sumstat)
				.join(
					(enter: any) =>
						enter
							.append('path')
							.attr('class', 'line')
							.attr('fill', 'none')
							.attr('stroke', (d: any) => color(d[0]))
							.attr('stroke-width', 1.5)
							.attr('clip-path', 'url(#clip)')
							.attr('d', (d: any) =>
								d3
									.line()
									.x((d: any) => xScale(new Date(d.timestamp)))
									.y((d: any) => yScale(+d.duration))(d[1])
							),
					(update: any) =>
						update
							.transition()
							.duration(animDuration)
							.attr('clip-path', 'url(#clip)')
							.attr('d', (d: any) =>
								d3
									.line()
									.x((d: any) => xScale(new Date(d.timestamp)))
									.y((d: any) => yScale(+d.duration))(d[1])
							),
					(exit: any) => exit.remove()
				);
		}

		// #endregion

		// #region Brush Chart
		
		// Brush function to zoom and pan chart
		function drawBrush() {
			// #region Initialize Brush Chart
			const margin_brush = { top: 0, right: 30, bottom: 25, left: 60 };
			d3.select('#brush').selectAll('*').remove();

			const width_brush  = container.node().getBoundingClientRect().width - margin_brush.left - margin_brush.right;
			const height_brush = 70 - margin_brush.top - margin_brush.bottom;

			// SVG element for brush chart
			const svg_brush = d3
				.select('#brush')
				.attr('viewBox', `0 0 ${width_brush + margin_brush.left + margin_brush.right} ${height_brush + margin_brush.top + margin_brush.bottom}`)
				.append('g')
				.attr('transform', `translate(${margin_brush.left},${margin_brush.top})`);

			// regular x-scale for chart
			let xScale_brush = d3
				.scaleTime()
				.range([0, width_brush])
				.domain(d3.extent(data, (d: any) => d.date));
			
			// const for calculating
			const const_xScale_brush = d3
				.scaleTime()
				.range([0, width_brush])
				.domain(d3.extent(data, (d: any) => d.date));

			// y-scale needed for lines
			let yScale_brush = d3
				.scaleLinear()
				.range([height_brush, 0])
				.domain([0, d3.max(data, (d: any) => d.duration)])
				.nice();

			// x-axis
			let xAxis_brush = svg_brush
				.append('g')
				.attr('transform', `translate(0,${height_brush})`)
				.style('font-size', '14px')
				.call(d3.axisBottom(xScale_brush)
						.tickValues(xScale_brush.ticks(d3.timeMonth.every(2)))
						.tickFormat(d3.timeFormat('%b %Y'))
				)
				.call((g: any) => g.select('.domain').remove())
				.selectAll('.tick line')
					.style('stroke-opacity', 0);
			
			svg_brush.selectAll('.tick text').style('fill', '#777');

			// Draw grid lines
			svg_brush
				.selectAll('xGrid')
				.data(xScale_brush.ticks(20))
				.attr('class', 'x-grid')
				.join('line')
				.attr('x1', (d: any) => xScale_brush(d))
				.attr('x2', (d: any) => xScale_brush(d))
				.attr('y1', 0)
				.attr('y2', height_brush)
				.attr('stroke', '#e0e0e0')
				.attr('stroke-width', 0.5)
				.attr('stroke-opacity', 0.33);

			// Add border around brush chart
			svg_brush
				.append('rect')
				.attr('x', 0)
				.attr('y', 0)
				.attr('width', width_brush)
				.attr('height', height_brush)
				.attr('stroke', '#777')
				.attr('fill', 'none');

			// Group data by 'app' for line chart
			const sumstat = d3.group(filteredData, (d: any) => d.app);

			// Define color scale
			const color = d3
				.scaleOrdinal()
				.range([
					'#e41a1c',
					'#377eb8',
					'#4daf4a',
					'#984ea3',
					'#ff7f00',
					'#ffff33',
					'#a65628',
					'#f781bf',
					'#999999'
				]);
			
			// Draw lines in the brush chart
			svg_brush
				.selectAll('.line')
				.data(sumstat)
				.join(
					(enter: any) =>
						enter
							.append('path')
							.attr('class', 'line')
							.attr('fill', 'none')
							.attr('stroke', (d: any) => color(d[0]))
							.attr('stroke-width', 1.5)
							.attr('clip-path', 'url(#clip)')
							.attr('d', (d: any) => d3
									.line()
									.x((d: any) => xScale_brush(new Date(d.timestamp)))
									.y((d: any) => yScale_brush(+d.duration))(d[1])
							),
					(update: any) =>
						update
							.transition()
							.duration(animDuration)
							.attr('clip-path', 'url(#clip)')
							.attr('d', (d: any) => d3
									.line()
									.x((d: any) => xScale_brush(new Date(d.timestamp)))
									.y((d: any) => yScale_brush(+d.duration))(d[1])
							),
					(exit: any) => exit.remove()
				);

			// #endregion

			// #region Brush functionality
			const brush = d3
				.brushX()
				.extent([
					[0, 0],
					[width_brush, height_brush]
				])
				.on('brush end', brushed);

			// Append brush group
			const brushGroup = svg_brush.append('g').attr('class', 'brush').call(brush);
			
			// Brush Event Handlers
			function brushed({ selection }: { selection: [number, number] | null }) {
				if (!selection) return;

				// Invert selection to date range
				const x0 = const_xScale_brush.invert(selection[0]);
				const x1 = const_xScale_brush.invert(selection[1]);
				
				start_date_label = x0.toISOString().split('T')[0];
				end_date_label = x1.toISOString().split('T')[0];

				// Update main chart with the selected range
				updateChart(x0, x1);

				// Update x-axis to reflect new domain
				xScale_brush.domain([x0, x1]);
				xAxis_brush.call(d3
						.axisBottom(xScale_brush)
						.tickValues(xScale_brush.ticks(d3.timeMonth.every(2)))
						.tickFormat(d3.timeFormat('%b %Y'))
				);
			}

			// Reset chart on double-click
			svg_brush.on('dblclick', () => {
				const fullExtent = d3.extent(data, (d: any) => d.date) as [string, string];

				// Reset xScale_brush and main chart
				xScale_brush.domain(fullExtent);

				start_date_label = new Date(fullExtent[0]).toISOString().split('T')[0];
				end_date_label = new Date(fullExtent[1]).toISOString().split('T')[0];
				updateChart(fullExtent[0], fullExtent[1]);

				// Clear brush selection
				brushGroup.call(brush.move, null);

				// Reset x-axis
				xAxis_brush.call(
					d3
						.axisBottom(xScale_brush)
						.tickValues(xScale_brush.ticks(d3.timeMonth.every(2)))
						.tickFormat(d3.timeFormat('%b %Y'))
				);
				// #endregion
			});
		}

		// #endregion
	}
</script>

<div id="container">
	<div class="my-2 flex justify-center gap-4" style="color: #777;">
		<span>Start Date: {start_date_label}</span>
		<span>End Date: {end_date_label}</span>
	</div>
	<svg id="brush"></svg>
	<svg id="chart"></svg>
	<div id="tooltip"></div>
</div>

<style>
</style>
