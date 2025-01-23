<script lang="ts">
	// @ts-ignore
	import * as d3 from 'd3';
	import { onMount } from 'svelte';
	import { type AppUsageData, type AppList, type margin } from './load';

	let { data, app_list }: { data: AppUsageData[] | null; app_list: AppList[] | null } = $props();
	let notice = "(2024-06-13 -- 2024-06-19 doesn't exist)";

	// TODO: calculating start and end dates insted of using this hardcoded values
	// d3.extent(data, (d: any) => d.date)[0], // Start date
	// d3.extent(data, (d: any) => d.date)[1]  // End date
	let start_date = $state('1999-01-01');
	let end_date = $state('2050-01-01');
	let animDuration = 10;

	let filteredData = $derived(
		data?.filter((d: any) => {
			return d.date >= new Date(start_date) && d.date <= new Date(end_date);
		})
	);

	$effect(() => {
		drawChart();
	});

	// TODO: double-click to reset zoom

	function drawChart() {
		// #region Main chart
		d3.select('#chart').selectAll('*').remove();

		const container = d3.select('#container');
		if (!container) throw new Error('Container not found');

		const margin: margin = { top: 10, right: 30, bottom: 30, left: 60 };
		const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
		const height = 400 - margin.top - margin.bottom;

		drawBrush();

		// #region draw chart
		// Initialize SVG element
		let svg = d3
			.select('#chart')
			.attr(
				'viewBox',
				`0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`
			)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Create clipping path to clip lines within the chart bounds.
		svg
			.append('defs')
			.append('clipPath')
			.attr('id', 'clip')
			.append('rect')
			.attr('width', width)
			.attr('height', height);

		// Group data by 'app' (to separate lines per app).
		const sumstat = d3.group(filteredData, (d: any) => d.app);

		// Color scale for different 'app' categories.
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

		// Time scale for x-axis.
		let xScale = d3
			.scaleTime()
			.range([0, width])
			.domain(d3.extent(filteredData, (d: any) => d.date));

		// Linear scale for y-axis (duration).
		let yScale = d3
			.scaleLinear()
			.range([height, 0])
			.domain([0, d3.max(data, (d: any) => d.duration)])
			.nice();

		// Create x-axis with custom tick formatting.
		let xAxis = svg
			.append('g')
			.attr('class', 'x-axis')
			.attr('transform', `translate(0,${height})`)
			.style('font-size', '14px')
			.call(
				d3
					.axisBottom(xScale)
					.ticks(10) // better?
					// .tickValues(xScale.ticks(d3.timeMonth.every(2))) // old way to manage ticks
					.tickFormat(d3.timeFormat('%b %Y'))
			)
			.call((g: any) => g.select('.domain').remove())
			.selectAll('.tick line')
			.style('stroke-opacity', 0);

		// Create y-axis.
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

		// Draw the lines for each 'app' in the dataset.
		svg
			.selectAll('.line')
			.data(sumstat, (d: any) => d[0])
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

		// #region draw tooltip
		// Set up the tooltip elements
		const tooltipLine = svg
			.append('line')
			.attr('stroke', '#fff')
			.attr('stroke-width', 1)
			.attr('opacity', 0);
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

		const listeningRect = svg
			.append('rect')
			.attr('width', width)
			.attr('height', height)
			.attr('opacity', 0)
			.on('mousemove', drawTooltip)
			.on('mouseout', removeTooltip);

		// Tooltip logic for displaying app-specific data.
		function drawTooltip(event: any) {
			const [mouseXsvg, mouseYsvg] = d3.pointer(event);
			const mouseX = event.clientX;
			const mouseY = event.clientY;

			// Get the closest data points for each line
			const points = Array.from(sumstat, ([key, values]) => {
				const closest = d3.least(values, (d) => Math.abs(xScale(d.date) - mouseXsvg));
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

			if (points.length === 0) return;

			// Tooltip positioning
			const tooltipWidth = tooltip.node()?.offsetWidth || 0;
			const tooltipHeight = tooltip.node()?.offsetHeight || 0;

			let tooltipLeft = mouseX + 20;
			let tooltipTop = mouseY - 40;

			// Ensure the tooltip stays within viewport bounds
			if (tooltipLeft + tooltipWidth > window.innerWidth) tooltipLeft = mouseX - tooltipWidth - 10;
			if (tooltipTop + tooltipHeight > window.innerHeight) tooltipTop = mouseY - tooltipHeight - 10;

			tooltip.style('left', `${tooltipLeft}px`).style('top', `${tooltipTop}px`).style('opacity', 1);

			// Build tooltip content
			const maxDuration = Math.max(...points.map((p) => p.duration));
			const tooltipContent = `
                <div><strong>Date:</strong> ${d3.timeFormat('%b %d, %Y')(points[0]?.date)}</div>
                <hr> ${points.map((p) => `
                    <div>
                        <strong style="color:${p.color}">${p.app}</strong><br>
                        Duration: ${p.duration === maxDuration
						? `<strong style="color: white">${p.duration} Hours</strong>`
						: `${p.duration} Hours`}
                    </div>`).join('')}`;
			tooltip.html(tooltipContent);

			// Update tooltip line
			tooltipLine
				.attr('x1', mouseXsvg)
				.attr('x2', mouseXsvg)
				.attr('y1', 0)
				.attr('y2', height)
				.attr('stroke-width', 1)
				.attr('opacity', 0.2);

			// Update or create circles
			const circles = svg.selectAll('.tooltip-circle').data(points, (d) => d.app);

			circles.exit().remove(); // Remove unneeded circles

			circles
				.attr('cx', (d) => d.x)
				.attr('cy', (d) => d.y)
				.attr('r', 4)
				.attr('fill', (d) => d.color);

			circles
				.enter()
				.append('circle')
				.attr('class', 'tooltip-circle')
				.attr('cx', (d) => d.x)
				.attr('cy', (d) => d.y)
				.attr('r', 4)
				.attr('fill', (d) => d.color);
		}

		// Remove tooltip on mouse out
		function removeTooltip() {
			tooltip.style('opacity', 0); // Hide tooltip
			tooltipLine.attr('opacity', 0); // Hide tooltip line
			svg.selectAll('.tooltip-circle').remove(); // Remove circles
		}

		// #endregion
		// #endregion

		// #region brush chart

		function updateChart(start: string, end: string) {
			const newDomain = [new Date(start), new Date(end)];
			// const newDomain = [new Date(start_date), new Date(end_date)];
			xScale.domain(newDomain);

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

			svg
				.select('.x-axis')
				.call(
					d3
						.axisBottom(xScale)
						.tickValues(xScale.ticks(tickInterval))
						.tickFormat(d3.timeFormat('%b %Y'))
				)
				.call((g) => g.select('.domain').remove())
				.selectAll('.tick line')
				.style('stroke-opacity', 0);
			

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
							.attr('x1', (d) => xScale(d))
							.attr('x2', (d) => xScale(d)),
					(exit: any) => exit.remove()
				);

			svg.selectAll('.tick text').style('fill', '#777');

			svg
				.selectAll('.line')
				.data(sumstat)
				.join(
					(enter: any) =>
						enter
							.append('path')
							.attr('class', 'line')
							.attr('fill', 'none')
							.attr('stroke', (d) => color(d[0]))
							.attr('stroke-width', 1.5)
							.attr('clip-path', 'url(#clip)')
							.attr('d', (d) =>
								d3
									.line()
									.x((d) => xScale(new Date(d.timestamp)))
									.y((d) => yScale(+d.duration))(d[1])
							),
					(update: any) =>
						update
							.transition()
							.duration(animDuration)
							.attr('clip-path', 'url(#clip)')
							.attr('d', (d) =>
								d3
									.line()
									.x((d) => xScale(new Date(d.timestamp)))
									.y((d) => yScale(+d.duration))(d[1])
							),
					(exit: any) => exit.remove()
				);
		}

		// Brush function to zoom and pan chart
		function drawBrush() {
			// #region draw brush chart
			const margin_brush = { top: 0, right: 30, bottom: 25, left: 60 };
			d3.select('#brush').selectAll('*').remove();

			const width_brush  = container.node().getBoundingClientRect().width - margin_brush.left - margin_brush.right;
			const height_brush = 70 - margin_brush.top - margin_brush.bottom;

			const svg_brush = d3
				.select('#brush')
				.attr('viewBox', `0 0 ${width_brush + margin_brush.left + margin_brush.right} ${height_brush + margin_brush.top + margin_brush.bottom}`)
				.append('g')
				.attr('transform', `translate(${margin_brush.left},${margin_brush.top})`);

			let xScale_brush = d3
				.scaleTime()
				.range([0, width_brush])
				.domain(d3.extent(data, (d: any) => d.date));
			const const_xScale_brush = d3
				.scaleTime()
				.range([0, width_brush])
				.domain(d3.extent(data, (d: any) => d.date));

			let yScale_brush = d3
				.scaleLinear()
				.range([height_brush, 0])
				.domain([0, d3.max(data, (d) => d.duration)])
				.nice();

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

			const xBGrid = svg_brush
				.selectAll('xGrid')
				.data(xScale_brush.ticks())
				.attr('class', 'x-grid')
				.join('line')
				.attr('x1', (d: any) => xScale_brush(d))
				.attr('x2', (d: any) => xScale_brush(d))
				.attr('y1', 0)
				.attr('y2', height_brush)
				.attr('stroke', '#e0e0e0')
				.attr('stroke-width', 0.5)
				.attr('stroke-opacity', 0.33);

			svg_brush
				.append('rect')
				.attr('x', 0)
				.attr('y', 0)
				.attr('width', width_brush)
				.attr('height', height_brush)
				.attr('stroke', '#777')
				.attr('fill', 'none');

			// Draw overall data line in brush chart
			// svg_brush
			// 	.append('path')
			// 	.attr('class', 'brush-line')
			// 	.attr('fill', 'none')
			// 	.attr('stroke', '#377eb8') // Use a neutral color
			// 	.attr('stroke-width', 1)
			// 	.attr('d', 
			// 		d3.line()
			// 			.x((d: any) => xScale_brush(d.date))
			// 			.y((d: any) => yScale_brush(d.duration))(data)
			// 	);

			// Group data by 'app' (to separate lines per app).
			const sumstat = d3.group(filteredData, (d: any) => d.app);

			// Color scale for different 'app' categories.
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
			svg_brush
				.selectAll('.line')
				.data(sumstat)
				.join(
					(enter: any) =>
						enter
							.append('path')
							.attr('class', 'line')
							.attr('fill', 'none')
							.attr('stroke', (d) => color(d[0]))
							.attr('stroke-width', 1.5)
							.attr('clip-path', 'url(#clip)')
							.attr('d', (d) =>
								d3
									.line()
									.x((d) => xScale_brush(new Date(d.timestamp)))
									.y((d) => yScale_brush(+d.duration))(d[1])
							),
					(update: any) =>
						update
							.transition()
							.duration(animDuration)
							.attr('clip-path', 'url(#clip)')
							.attr('d', (d) =>
								d3
									.line()
									.x((d) => xScale_brush(new Date(d.timestamp)))
									.y((d) => yScale_brush(+d.duration))(d[1])
							),
					(exit: any) => exit.remove()
				);

			const brush = d3
				.brushX()
				.extent([
					[0, 0],
					[width_brush, height_brush]
				])
				.on('brush end', brushed);

			// Append brush group for???
			const brushGroup = svg_brush.append('g').attr('class', 'brush').call(brush);
			// #endregion

			// #region brush area
			// function brushed({ selection }) {
			// 	if (!selection) return;
			// 	// The selection is in pixel space, so we use xScale_brush to map it to the domain
			// 	const [x0, x1] = selection;
				
			// 	start_date = xScale_brush.invert(x0).toISOString().split('T')[0];
			// 	end_date = xScale_brush.invert(x1).toISOString().split('T')[0];

				
			// 	svg.selectAll('.tooltip-circle').remove();
			// 	updateChart();
			// }

			function brushed({ selection }) {
				if (!selection) return;
				console.log('Selection:', selection); // Logs the selected pixel coordinates

				// full date time gmt
				const x0 = const_xScale_brush.invert(selection[0]);
				const x1 = const_xScale_brush.invert(selection[1]);
				console.log('X0 and X1:', x0, x1);
				
				// date only
				let start = x0.toISOString().split('T')[0];
				let end = x1.toISOString().split('T')[0];
				console.log('start and end:', start, end);

				// update main chart
				updateChart(x0, x1);

				

				// Update the xScale domain
				xScale_brush.domain([x0, x1]);

				// Update the x-axis
				xAxis_brush.call(
					d3
						.axisBottom(xScale_brush)
						.tickValues(xScale_brush.ticks(d3.timeMonth.every(2)))
						.tickFormat(d3.timeFormat('%b %Y'))
				);

				// Update the brushed area (optional)
				svg_brush.selectAll('.x-grid').remove();
			}
			// #endregion

			svg_brush.on('dblclick', () => {
				// Reset the xScale_brush domain to the full extent of the data
				xScale_brush.domain(d3.extent(data, (d: any) => d.date));

				// Update the x-axis to reflect the reset domain
				xAxis_brush.call(
					d3
						.axisBottom(xScale_brush)
						.tickValues(xScale_brush.ticks(d3.timeMonth.every(2)))
						.tickFormat(d3.timeFormat('%b %Y'))
				);

				// Clear any active brush selection
				brushGroup.call(brush.move, null);

				// Update the main chart with the full data extent
				updateChart(
					d3.extent(data, (d: any) => d.date)[0], // Start date
					d3.extent(data, (d: any) => d.date)[1]  // End date
				);
			});
		}
	}
</script>

<div id="container">
	<div class="my-2 flex justify-center gap-4" style="color: #777;">
		<span>Start Date: {start_date}</span>
		<span>End Date: {end_date}</span>
	</div>
	<svg id="brush"></svg>
	<svg id="chart"></svg>
	<div id="tooltip"></div>

	<!-- <div id="modal" class="modal" class:visible={isModalVisible} onclick={hideModal}>
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
    </div> -->
</div>

<style>
</style>
