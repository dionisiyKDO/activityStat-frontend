<script lang="ts">
	// @ts-nocheck
	import * as d3 from 'd3';
	import {
		chartFontSize,
		chartColor,
		chartStroke,
		chartStrokeWidth,
		chartStrokeOpacity,
		chartBar,
		tooltipFontSize,
		tooltipColor,
		tooltipBG,
		tooltipBorder,
		tooltipBorderRadius,
		tooltipPadding,
		tooltipBoxShadow
	} from '$lib/chartStyles';

	interface Props {
		data: any[];
	}

	let { data }: Props = $props();

	let chartContainer: HTMLDivElement;
	let chartSvg: SVGSVGElement;
	let resizeObserver: ResizeObserver;
	let tooltip: d3.Selection<HTMLDivElement, unknown, null, undefined>;

	function drawChart() {
		if (!chartContainer || !chartSvg || !data.length) return;

		// Clear previous chart
		d3.select(chartSvg).selectAll('*').remove();

		// Get actual container dimensions
		const containerRect = chartContainer.getBoundingClientRect();
		const margin = { top: 10, right: 10, bottom: 100, left: 80 }; // const margin = { top: 10, right: 60, bottom: 100, left: 60 };
		const width = containerRect.width - margin.left - margin.right;
		const chartHeight = 550;
		const height = chartHeight - margin.top - margin.bottom;

		if (width <= 0 || height <= 0) return;

		const filter_threshold = 50;

		// Set up SVG with proper dimensions
		const svg = d3
			.select(chartSvg)
			.attr('width', containerRect.width)
			.attr('height', chartHeight)
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Create scales
		const xScale = d3
			.scaleBand()
			.domain(data.filter((d) => d.duration > filter_threshold).map((d) => d.title))
			.range([0, width])
			.padding(0.1);

		const yScale = d3
			.scaleLinear()
			.domain([0, d3.max(data, (d) => d.duration) || 0])
			.range([height, 0])
			.nice();

		// Add axes
		const xAxis = svg
			.append('g')
			.attr('class', 'x-axis')
			.attr('transform', `translate(0,${height})`)
			.style('font-size', chartFontSize)
			.style('color', chartColor)
			.call(d3.axisBottom(xScale))
			.call((g) => g.select('.domain').remove());

		xAxis.selectAll('.tick line').style('stroke', chartStroke).style('stroke-opacity', 0);

		xAxis
			.selectAll('.tick text')
			.style('text-anchor', 'end')
			.attr('transform', 'rotate(-30)')
			.attr('dx', '-0.5em')
			.attr('dy', '0.15em');

		svg
			.append('g')
			.attr('class', 'y-axis')
			.style('font-size', chartFontSize)
			.style('color', chartColor)
			.call(d3.axisLeft(yScale))
			.call((g) => g.select('.domain').remove())
			.selectAll('.tick line')
			.style('stroke', chartStroke)
			.style('stroke-opacity', 0);

		// Add grid lines (y-axis only for bar charts)
		svg
			.selectAll('.y-grid')
			.data(yScale.ticks().slice(1))
			.join('line')
			.attr('class', 'y-grid')
			.attr('x1', 0)
			.attr('x2', width)
			.attr('y1', (d) => yScale(d))
			.attr('y2', (d) => yScale(d))
			.attr('stroke', chartStroke)
			.attr('stroke-width', chartStrokeWidth)
			.attr('stroke-opacity', chartStrokeOpacity);

		// Add chart border
		svg
			.append('rect')
			.attr('x', 0)
			.attr('y', 0)
			.attr('width', width)
			.attr('height', height)
			.attr('stroke', chartStroke)
			.attr('stroke-width', chartStrokeWidth)
			.attr('fill', 'none');

		// Create the bars
		svg
			.selectAll('.bar')
			.data(data.filter((d) => d.duration > filter_threshold))
			.join('rect')
			.attr('class', 'bar')
			.attr('x', (d) => xScale(d.title) || 0)
			.attr('y', (d) => yScale(d.duration))
			.attr('width', xScale.bandwidth())
			.attr('height', (d) => height - yScale(d.duration))
			.attr('fill', chartBar)
			.on('mouseover', function (event, d) {
				// Highlight bar on hover
				d3.select(this).attr('opacity', 0.8);
				showTooltip(event, d);
			})
			.on('mousemove', function (event, d) {
				showTooltip(event, d);
			})
			.on('mouseout', function () {
				// Remove highlight
				d3.select(this).attr('opacity', 1);
				hideTooltip();
			});

		function showTooltip(event: MouseEvent, d: any) {
			const [mouseXsvg, mouseYsvg] = d3.pointer(event);

			// Position and show tooltip
			const tooltipContent = `In ${d.title}<br/>${d.duration} Hours`;

			tooltip.style('opacity', 1).html(tooltipContent);

			const tooltipNode = tooltip.node() as HTMLElement;
			const tooltipRect = tooltipNode.getBoundingClientRect();

			let left = event.clientX + 15;
			let top = event.clientY - 15;

			// Adjust if tooltip goes off screen
			if (left + tooltipRect.width > window.innerWidth) {
				left = event.clientX - tooltipRect.width - 15;
			}
			if (top + tooltipRect.height > window.innerHeight) {
				top = event.clientY - tooltipRect.height - 15;
			}

			tooltip.style('left', `${left}px`).style('top', `${top}px`);
		}

		function hideTooltip() {
			tooltip.style('opacity', 0);
		}
	}

	function setupResizeObserver() {
		if (resizeObserver) {
			resizeObserver.disconnect();
		}

		resizeObserver = new ResizeObserver(() => {
			drawChart();
		});

		if (chartContainer) {
			resizeObserver.observe(chartContainer);
		}
	}

	function initializeTooltip() {
		tooltip = d3
			.select('body')
			.append('div')
			.attr('class', 'chart-tooltip')
			.style('position', 'fixed')
			.style('z-index', '1000')
			.style('pointer-events', 'none')
			.style('background-color', tooltipBG)
			.style('border', tooltipBorder)
			.style('font-size', tooltipFontSize)
			.style('color', tooltipColor)
			.style('padding', tooltipPadding)
			.style('border-radius', tooltipBorderRadius)
			.style('box-shadow', tooltipBoxShadow)
			.style('opacity', 0);
	}

	function cleanup() {
		if (resizeObserver) {
			resizeObserver.disconnect();
		}
		if (tooltip) {
			tooltip.remove();
		}
	}

	$effect(() => {
		if (chartContainer) {
			initializeTooltip();
			setupResizeObserver();
			drawChart();
		}

		return cleanup;
	});
</script>

<div bind:this={chartContainer} class="chart-container h-full w-full">
	<svg bind:this={chartSvg} class="w-full"></svg>
</div>
