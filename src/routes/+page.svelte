<script lang="ts">
	// @ts-ignore
	import * as d3 from 'd3';
	import { onMount } from 'svelte';

	let svg: HTMLElement;
	let data = []; // Default data (current year or range)
	let allData = {}; // Store data for multiple years
	let currentYear = 2025; // Default year

	// Generate datasets for multiple years
	const generateYearData = (year: number) => {
		const data = [];
		const startDate = new Date(`${year}-01-01`);
		const endDate = new Date(`${year}-12-31`);
		let currentDate = startDate;

		while (currentDate <= endDate) {
			data.push({
				date: currentDate.toISOString().split('T')[0], // Format YYYY-MM-DD
				value: Math.floor(Math.random() * 10) // Random value between 0 and 9
			});
			currentDate.setDate(currentDate.getDate() + 1);
		}

		return data;
	};

	const datasets: any = $state({
		2025: generateYearData(2025),
		2024: generateYearData(2024),
		2023: generateYearData(2023)
	});

	$inspect(datasets);

	// Initial render
	$effect(() => {
		updateGraph(datasets[currentYear]);
	});

	// #region Start

	function updateGraph(data: any) {
		const width = 900;
		const height = 200;
		const cellSize = 20;
		const margin = { top: 30, right: 60, bottom: 30, left: 40 };

		const parseDate = d3.timeParse('%Y-%m-%d');
		const formatDay = d3.timeFormat('%w'); // Day of the week (0-6)
		const formatWeek = d3.timeWeek.count; // Week number since start of the year
		const formatMonth = d3.timeFormat('%B'); // Full month name
		const formatDate = d3.timeFormat('%Y-%m-%d');

		const svgElement = d3
			.select(svg)
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom);

		svgElement.selectAll('*').remove(); // Clear previous graph

		const g = svgElement.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);

		// Prepare data for rendering
		const parsedData = data.map((d) => ({
			...d,
			date: parseDate(d.date)
		}));
		// Get the first and last date to determine weeks and months
		const firstDate = d3.min(parsedData, (d) => d.date);
		const lastDate = d3.max(parsedData, (d) => d.date);

		// Create color scale
		const colorScale = d3
			.scaleSequential(d3.interpolateBlues)
			.domain([0, d3.max(parsedData, (d) => d.value)]);

		// Add cells (chronologically correct placement)
		g.selectAll('rect')
			.data(parsedData)
			.enter()
			.append('rect')
			.attr('x', (d) => formatWeek(firstDate, d.date) * cellSize) // Week number since start
			.attr('y', (d) => formatDay(d.date) * cellSize) // Day of the week
			.attr('width', cellSize - 2)
			.attr('height', cellSize - 2)
			.attr('rx', 4)
			.attr('fill', (d) => colorScale(d.value))
			.attr('stroke', '#ccc')
			.on('mouseover', function (event, d) {
				d3.select(this).attr('stroke', '#000').attr('stroke-width', 2);
				tooltip
					.style('visibility', 'visible')
					.html(
						`<div><strong>Date:</strong> ${formatDate(d.date)}</div>
           <div><strong>Value:</strong> ${d.value}</div>`
					)
					.style('left', event.pageX + 10 + 'px')
					.style('top', event.pageY - 28 + 'px');
			})
			.on('mouseout', function () {
				d3.select(this).attr('stroke', '#ccc').attr('stroke-width', 1);
				tooltip.style('visibility', 'hidden');
			});

		// Add Y-axis labels (days)
		const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
		g.selectAll('text.day-label')
			.data(days)
			.enter()
			.append('text')
			.attr('class', 'day-label')
			.text((d) => d)
			.attr('x', -10)
			.attr('y', (d, i) => i * cellSize + cellSize / 1.5)
			.attr('text-anchor', 'end')
			.attr('fill', '#333')
			.attr('font-size', 12);

		// Add X-axis labels (months)
		const months = d3.timeMonths(firstDate, d3.timeMonth.offset(lastDate, 1));
		g.selectAll('text.month-label')
			.data(months)
			.enter()
			.append('text')
			.attr('class', 'month-label')
			.text((d) => formatMonth(d))
			.attr(
				'x',
				(d) => formatWeek(firstDate, d) * cellSize + cellSize / 2 // Centered on the first week of the month
			)
			.attr('y', -10)
			.attr('text-anchor', 'start')
			.attr('fill', '#333')
			.attr('font-size', 12);

		// Tooltip
		const tooltip = d3
			.select('body')
			.append('div')
			.attr('class', 'tooltip')
			.style('position', 'absolute')
			.style('visibility', 'hidden')
			.style('background', 'rgba(0, 0, 0, 0.8)')
			.style('color', '#fff')
			.style('padding', '8px 12px')
			.style('border-radius', '4px')
			.style('font-size', '12px')
			.style('pointer-events', 'none');
	}


	// Switch year
	const switchYear = (year) => {
		currentYear = year;
		updateGraph(datasets[year]);
	};
</script>

<div class="controls">
	{#each Object.keys(datasets) as year}
		<button on:click={() => switchYear(year)}>
			{year}
		</button>
	{/each}
</div>

<svg bind:this={svg} width="850" height="300"></svg>

<style>
	svg {
		font-family: Arial, sans-serif;
	}

	.controls {
		margin-bottom: 10px;
	}

	.controls button {
		margin-right: 10px;
		padding: 5px 10px;
		border: none;
		background: #007bff;
		color: white;
		cursor: pointer;
		border-radius: 4px;
		font-size: 14px;
	}

	.controls button:hover {
		background: #0056b3;
	}

	.tooltip {
		pointer-events: none;
	}
</style>
