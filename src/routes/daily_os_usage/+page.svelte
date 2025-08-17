<!-- routes/daily_os_usage/+page.svelte -->
<script lang="ts">
	import LineChart from '$lib/OSUsageTime/LineChart.svelte';
	import { fetchAppOSData } from './load';
	import { type OSUsageData } from '$lib/types';

	let osUsageDataReq: Promise<OSUsageData[] | null> | null = $state(null);

	osUsageDataReq = fetchAppOSData();
</script>

<!-- Container -->
<div class="mt-4 flex flex-col gap-4">
	<h1 class="text-3xl font-bold text-[--primary-text]">OS Usage Analytics</h1>

	<!-- Charts -->
	<div class="surface">
		{#await osUsageDataReq}
			<div class="flex items-center justify-center p-6 text-4xl">
				<p class="loading">Loading os data...</p>
			</div>
		{:then data}
			<LineChart {data}/>
		{:catch error}
			<p class="error">{error.message}</p>
		{/await}
	</div>
</div>
