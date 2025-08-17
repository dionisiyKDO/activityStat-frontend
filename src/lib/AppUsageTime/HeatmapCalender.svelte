<script lang="ts">
	// @ts-ignore
	import * as d3 from 'd3';
	import { type AppUsageData, type margin } from '$lib/types';

	// #region Data Preparation
	let chartContainer: HTMLDivElement;
	let chartSvg: SVGSVGElement;
	let tooltipDiv: HTMLDivElement;

	let { data }: { data: AppUsageData[] | null } = $props();

	let datasets = $derived(groupByYear(data));
	let currentYear = $state(new Date().getFullYear());
	let clampValue = $state(2.5); // Threshold for cell color max range value

	function groupByYear(data: AppUsageData[] | null) {
		if (!data?.length) return {};

		const result: Record<number, { date: string; duration: number }[]> = {};

		// First pass: aggregate existing data by date
		const dateAggregates: Record<string, number> = {};
		data.forEach((d) => {
			if (d.date) {
				const date = d.date.toISOString().split('T')[0]
				dateAggregates[date] = (dateAggregates[date] || 0) + d.duration;
			}
		});

		// Second pass: create complete year datasets
		Object.keys(dateAggregates).forEach((date) => {
			const year = new Date(date).getFullYear();

			if (!result[year]) {
				result[year] = generateFullYearDates(year);
			}

			const existingEntry = result[year].find((item) => item.date === date);
			if (existingEntry) {
				existingEntry.duration = Number(dateAggregates[date].toFixed(2));
			}
		});

		return result;
	}

	function generateFullYearDates(year: number) {
		const dates = [];
		const startDate = new Date(year, 0, 1);
		const endDate = new Date(year, 11, 31);

		for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
			dates.push({
				date: d.toISOString().split('T')[0],
				duration: 0
			});
		}

		return dates;
	}

	// #endregion

	$effect(() => {
		if (datasets && datasets[currentYear]) {
			drawHeatmap(datasets[currentYear]);
		}
	});

	$effect(() => {
		if (!chartContainer) return;

		const resizeObserver = new ResizeObserver(() => {
			if (datasets && datasets[currentYear]) {
				drawHeatmap(datasets[currentYear]);
			}
		});

		resizeObserver.observe(chartContainer);
		return () => resizeObserver.disconnect();
	});

	function drawHeatmap(data: any) {
		//#region Draw Heatmap
		if (!chartContainer || !chartSvg || !data?.length) return;
		d3.select(chartSvg).selectAll('*').remove();

		// Chart configuration
		const cellMargin = 1;
		const cellStrokeWidth = 2;
		const cellBorderRadius = 4;
		const margin: margin = { top: 30, right: 60, bottom: 30, left: 40 };
		const height = 200;

		// const cellSize = 20;
		// const width = 1100;

		const containerRect = chartContainer.getBoundingClientRect();
		const availableWidth = containerRect.width;
		const cellSize = Math.min(20, availableWidth / 56); // ~53 weeks + margins
		const width = Math.min(availableWidth, cellSize * 53 + margin.left + margin.right);

		// Colors and styles
		const startColor = '#242424'; // background color
		const endColor = '#f0e68c'; // light khaki | #535bf2 | 'rgba(0, 0, 0, 0)'
		const accentColor = 'black';
		const cellStrokeColor = 'rgba(100, 100, 100, 0.5)';
		const cellStrokeColorFocus = '#f0e68c';
		const textColor = '#777';
		const fontSize = 14;

		// Date formatters
		const parseDate = d3.timeParse('%Y-%m-%d');
		const formatDay = d3.timeFormat('%w'); // Day of the week (0-6)
		const formatWeek = d3.timeWeek.count; // Week number since start of the year
		const formatMonth = d3.timeFormat('%B'); // Full month name
		const formatDate = d3.timeFormat('%Y-%m-%d');

		// Parse and prepare data
		const parsedData = data.map((d: any) => ({
			...d,
			date: parseDate(d.date)
		}));

		// Get the first and last date to determine weeks and months
		const firstDate = d3.min(parsedData, (d: any) => d.date);
		const lastDate = d3.max(parsedData, (d: any) => d.date);

		// #region Start drawing

		// Initialize SVG element
		const svg = d3
			.select(chartSvg)
			.attr('width', width)
			.attr('height', height)
			.append('g')
			.attr('transform', `translate(${margin.left}, ${margin.top})`);

		// Create color scale for cell values
		const colorScale = d3
			.scaleLinear<string>()
			.domain([0, clampValue])
			.range([startColor, endColor])
			.clamp(true);

		// Add Y-axis labels (days)
		const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
		svg
			.selectAll('text.day-label')
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
		svg
			.selectAll('text.month-label')
			.data(months)
			.enter()
			.append('text')
			.attr('class', 'month-label')
			.text((d: any) => formatMonth(d))
			.attr('x', (d: any) => formatWeek(firstDate, d) * cellSize + cellSize / 4) // 'Centered' on the first day of the month (formatWeek(firstDate, d) * cellSize), but slightly shifted to the right ( + cellSize / 4)
			.attr('y', -10)
			.attr('text-anchor', 'start')
			.attr('fill', textColor)
			.attr('font-size', fontSize);

		// #region Draw cells
		// Add cells (chronologically correct placement)
		svg
			.selectAll('rect')
			.data(parsedData)
			.enter()
			.append('rect')
			.attr('x', (d: any) => formatWeek(firstDate, d.date) * cellSize) // Week number since start
			.attr('y', (d: any) => formatDay(d.date) * cellSize) // Day of the week
			.attr('width', cellSize - cellStrokeWidth - cellMargin) // -2 for stroke(border)
			.attr('height', cellSize - cellStrokeWidth - cellMargin)
			.attr('rx', cellBorderRadius)
			.attr('fill', (d: any) => colorScale(d.duration))
			.attr('stroke', cellStrokeColor)
			.attr('stroke-width', 1)
			.style('cursor', 'pointer')
			// .on('mouseover', drawTooltip)
			// .on('mouseout', removeTooltip);
			.on('mouseover', function (this: any, event: MouseEvent, d: any) {
				// Highlight cell
				d3.select(this).attr('stroke', cellStrokeColorFocus).attr('stroke-width', 2);

				showTooltip(event, d);
			})
			.on('mouseout', function (this: any) {
				// Reset cell
				d3.select(this).attr('stroke', cellStrokeColor).attr('stroke-width', 1);

				hideTooltip();
			});

		// Add corner indicators for clamped values (separate from cells)
		svg
			.selectAll('circle.indicator')
			.data(parsedData.filter((d: any) => d.duration >= clampValue))
			.enter()
			.append('circle')
			.attr('class', 'indicator')
			.attr(
				'cx',
				(d: any) =>
					formatWeek(firstDate, d.date) * cellSize + cellSize - cellStrokeWidth - cellMargin - 3
			)
			.attr('cy', (d: any) => formatDay(d.date) * cellSize + 3)
			.attr('r', 2)
			.attr('fill', accentColor) // or 'red' if you prefer
			.style('pointer-events', 'none') // Don't interfere with cell interactions
			.raise(); // Ensure circles are on top of rectangles

		// #endregion

		// Tooltip
		const tooltip = d3
			.select(tooltipDiv)
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

		// Tooltip functions
		function showTooltip(event: MouseEvent, d: { date: Date; duration: number }) {
			const tooltip = d3.select(tooltipDiv);

			const tooltipWidth = tooltipDiv.offsetWidth + 20;
			const tooltipHeight = tooltipDiv.offsetHeight;
			let tooltipLeft = event.clientX + 10;
			let tooltipTop = event.clientY - 30;

			// Keep tooltip within viewport
			if (tooltipLeft + tooltipWidth > window.innerWidth) {
				tooltipLeft = event.clientX - tooltipWidth - 10;
			}
			if (tooltipTop + tooltipHeight > window.innerHeight) {
				tooltipTop = event.clientY - tooltipHeight - 10;
			}

			tooltip
				.style('visibility', 'visible')
				.html(
					`
					<div><strong>Date:</strong> ${formatDate(d.date)}</div>
					<div><strong>Hours:</strong> ${d.duration}</div>
				`
				)
				.style('left', `${tooltipLeft}px`)
				.style('top', `${tooltipTop}px`);
		}

		function hideTooltip() {
			d3.select(tooltipDiv).style('visibility', 'hidden');
		}
		// #endregion
	}

	// Switch year
	function switchYear(year: string) {
		const yearNum = parseInt(year);
		if (datasets[yearNum]) {
			currentYear = yearNum;
		}
	}
</script>

<!-- #region Tags
-->
<div class="mt-10 flex flex-col justify-center">
	<div bind:this={chartContainer} id="container" class="flex justify-center">
		<svg bind:this={chartSvg}></svg>
		<div bind:this={tooltipDiv}></div>
	</div>

	{#if datasets && Object.keys(datasets).length > 0}
		<div class="controls flex justify-center gap-2">
			{#each Object.keys(datasets!) as year}
				<button
					class="button {currentYear === parseInt(year) ? 'border-pink-400/40' : ''}"
					onclick={() => switchYear(year)}
				>
					{year}
				</button>
			{/each}

			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<div class="border-l border-solid border-[--border] pl-2">
				<div
					class="button flex w-20 cursor-text items-center justify-center gap-1"
					onclick={(e) => {
						const input = e.currentTarget.querySelector('input');
						input?.focus();
						input?.select();
					}}
				>
					<input
						type="text"
						bind:value={clampValue}
						class="w-8 border-none bg-transparent text-center text-white outline-none"
						style="color: inherit;"
						onkeydown={(e) => {
							// Allow only numbers, backspace, delete, arrow keys, and decimal point
							if (
								!/[\d\.\b]/.test(e.key) &&
								!['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab'].includes(e.key)
							) {
								e.preventDefault();
							}
						}}
					/>
					<span class="text-sm text-[--muted-text]">hrs</span>
				</div>
			</div>
		</div>
	{/if}
</div>
<!-- #endregion
-->
