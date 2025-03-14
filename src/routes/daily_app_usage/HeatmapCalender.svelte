<script lang="ts">
	// @ts-ignore
	import * as d3 from 'd3';
	import { onMount } from 'svelte';
	import { type AppUsageData, type margin } from './load';


    let { data }: { data: AppUsageData[] | null } = $props();
    let datasets = $derived(groupByYear(data));

    function groupByYear(data: AppUsageData[] | null) {
		const result = data?.reduce((acc: Record<number, { date: string, duration: number }[]>, d: AppUsageData) => {
			// Extract the year
			const date = new Date(d.timestamp).toISOString().split('T')[0];
			
			// Check if this year exists in the accumulator
			const year = new Date(date).getFullYear();
			if (!acc[year]) {
				// acc[year] = []; // If not, create an empty array for that year

				// Generate all dates for the entire year
				const startDate = new Date(year, 0, 2);
				const endDate = new Date(year, 11, 31);
				
				acc[year] = [];
				for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
					acc[year].push({ 
						date: d.toISOString().split('T')[0], 
						duration: 0 
					});
				}
			}	

			// Look for existing entry with same date
			const existingEntry = acc[year].find(item => item.date === date);
			if (existingEntry) { // If found, add current duration to existing entry
				existingEntry.duration = Number((existingEntry.duration + d.duration).toFixed(2));
			} else { // If not found, create new entry
				acc[year].push({ date, duration: Number((d.duration).toFixed(2)) });
			}

			return acc;
		}, {});

   		return result;
	}

	let svg: HTMLElement;
	let currentYear = 2024; // Default year

	// Initial render
	$effect(() => {
		updateGraph(datasets![currentYear]);
	});

	// #region Start

	// TODO: Refactor width, height and margins. Now graph just cuts out if goes out of bounds
    // TODO: if data is null, show empty chart, without color
	function updateGraph(data: any) {
		d3.select('#heatmap').selectAll('*').remove();

		const cellMargin = 1;
		const cellStrokeWidth = 2;
		const cellStrokeOpacity = 0.5;
		const cellStrokeColor = 'rgba(100, 100, 100, 0.5)';
		const cellStrokeColorFocus = '#f0e68c';

		const textColor = '#777';
		const fontSize = 14;

		const container = d3.select('#container');
		// const width = container.node().getBoundingClientRect().width;
		const width = 1100;
		const height = 200;
		const cellSize = 20;
		const margin: margin = { top: 30, right: 60, bottom: 30, left: 40 };

		let startColor = '#242424'; // background color
		let endColor = '#f0e68c'; // light khaki | #535bf2 | 'rgba(0, 0, 0, 0)'

		const parseDate = d3.timeParse('%Y-%m-%d');
		const formatDay = d3.timeFormat('%w'); // Day of the week (0-6)
		const formatWeek = d3.timeWeek.count; // Week number since start of the year
		const formatMonth = d3.timeFormat('%B'); // Full month name
		const formatDate = d3.timeFormat('%Y-%m-%d');

		// Prepare data for rendering
		const parsedData = data.map((d: any) => ({
			...d,
			date: parseDate(d.date)
		})); 

		// # Region Start drawing

		// Initialize SVG element
		const svg = d3
			.select('#heatmap')
			.attr('width', width)
			.attr('height', height)
			.append('g')
			.attr('transform', `translate(${margin.left}, ${margin.top})`);

		// Create color scale for cell values
		const colorScale = d3
			.scaleLinear()
			.domain([0, d3.max(data, (d: any) => d.duration) == 0 ? 1 : d3.max(data, (d: any) => d.duration)])
			.range([startColor, endColor]);
		
		// Get the first and last date to determine weeks and months
		const firstDate = d3.min(parsedData, (d: any) => d.date);
		const lastDate = d3.max(parsedData, (d: any) => d.date);


		// Add cells (chronologically correct placement)
		svg.selectAll('rect')
			.data(parsedData)
			.enter()
			.append('rect')
			.attr('x', (d: any) => formatWeek(firstDate, d.date) * cellSize) // Week number since start
			.attr('y', (d: any) => formatDay(d.date) * cellSize) // Day of the week
			.attr('width', cellSize - cellStrokeWidth - cellMargin) // -2 for stroke(border)
			.attr('height', cellSize - cellStrokeWidth - cellMargin)
			.attr('rx', 4)
			.attr('fill', (d: any) => colorScale(d.duration))
			.attr('stroke', cellStrokeColor)
			.on('mouseover', drawTooltip)
			.on('mouseout', removeTooltip);

		// #region Tooltip
		function drawTooltip(this: any, event: any, d: any) {
			d3.select(this).attr('stroke', cellStrokeColorFocus).attr('stroke-width', 2);
				
			// Tooltip positioning
			const tooltipWidth = tooltip.node()?.offsetWidth + 20 || 0; // 20 for browser scrollbar width
			const tooltipHeight = tooltip.node()?.offsetHeight || 0;
			let tooltipLeft = event.clientX + 10;
			let tooltipTop = event.clientY - 30;

			// Ensure the tooltip stays within viewport bounds
			if (tooltipLeft + tooltipWidth > window.innerWidth) tooltipLeft = event.clientX - tooltipWidth - 10;
			if (tooltipTop + tooltipHeight > window.innerHeight) tooltipTop = event.clientY - tooltipHeight - 10;

			tooltip
				.style('visibility', 'visible')
				.html(`	
					<div><strong>Date:</strong> ${formatDate(d.date)}</div>
					<div><strong>Hours:</strong> ${d.duration}</div>`
				)
				.style('left', `${tooltipLeft}px`)
				.style('top', `${tooltipTop}px`)
				.style('pointer-events', 'none');
		}

		function removeTooltip(this: any) {
			d3.select(this).attr('stroke', cellStrokeColor).attr('stroke-width', 1);
			tooltip.style('visibility', 'hidden');
		}
		// #endregion

		// Add Y-axis labels (days)
		const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
		svg.selectAll('text.day-label')
			.data(days)
			.enter()
			.append('text')
			.attr('class', 'day-label')
			.text((d: any) => d)
			.attr('x', -10)
			.attr('y', (d: any, i: any) => i * cellSize + cellSize / 1.5) // Kind of hard-coded positioning
			.attr('text-anchor', 'end')
			.attr('fill', textColor)
			.attr('font-size', fontSize);

		// Add X-axis labels (months)
		const months = d3.timeMonths(firstDate, lastDate); // d3.timeMonth.offset(lastDate, 1) - if you want to show one more month after december
		svg.selectAll('text.month-label')
			.data(months)
			.enter()
			.append('text')
			.attr('class', 'month-label')
			.text((d: any) => formatMonth(d))
			.attr('x',(d: any) => formatWeek(firstDate, d) * cellSize + cellSize / 4) // 'Centered' on the first day of the month (formatWeek(firstDate, d) * cellSize), but slightly shifted to the right ( + cellSize / 4)
			.attr('y', -10)
			.attr('text-anchor', 'start')
			.attr('fill', textColor)
			.attr('font-size', fontSize);

		// Tooltip
		const tooltip = d3
			.select('#heatmap-tooltip')
			.style('position', 'fixed')
			.style('white-space', 'nowrap')
			.style('z-index', '10')
			.style('visibility', 'hidden')
			.style('background', 'rgba(0, 0, 0, 0.8)')
			.style('color', '#fff')
			.style('padding', '8px 12px')
			.style('border', 'solid 1px #646cff')
			.style('border-radius', '6px')
			.style('font-size', '12px')
			.style('pointer-events', 'none');
	}


	// Switch year
	const switchYear = (year: any) => {
		currentYear = year;
		updateGraph(datasets![year]);
	};
</script>


<div class="mt-10 flex flex-col justify-center">
    <div id="container" class="flex justify-center">
        <svg id="heatmap"></svg>
		<div id="heatmap-tooltip" class="tooltip"></div>
    </div>
    
    <div class="controls flex gap-2 justify-center">
        {#each Object.keys(datasets!) as year}
            <button class="button" onclick={() => switchYear(year)}>
                {year}
            </button>
        {/each}
    </div>
</div>


<style>
</style>
