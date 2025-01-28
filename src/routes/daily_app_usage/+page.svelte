<script lang="ts">
	import { 
        fetchAppList, 
        fetchAppUsageData, 
        type App,
        type AppUsageData, 
    } from './load';
    import Chip from './Chip.svelte';
	import MultiSelect from "./MultiSelect.svelte";
	import HeatmapCalender from "./HeatmapCalender.svelte";
	import LineChart from './LineChart.svelte';

	// Presets
	const presets = [
		{
			"name": "Gi/HSR/ZZZ",	
			"preset": [
				{ app: 'GenshinImpact.exe', title: 'Genshin Impact' },
				{ app: 'StarRail.exe', title: 'Honkai: Star Rail' },
				{ app: 'ZenlessZoneZero.exe', title: 'Zenless Zone Zero' }
			],
		},
		{
			"name": "Gacha",
			"preset": [
				{
					"app": "GenshinImpact.exe",
					"title": "Genshin Impact"
				},
				{
					"app": "StarRail.exe",
					"title": "Honkai: Star Rail"
				},
				{
					"app": "ZenlessZoneZero.exe",
					"title": "Zenless Zone Zero"
				},
				{
					"app": "dnplayer.exe",
					"title": "LDPlayer"
				},
				{
					"app": "reverse1999.exe",
					"title": "Reverse 1999"
				},
				{
					"app": "Client-Win64-Shipping.exe",
					"title": "Wuthering Waves"
				},
				{
					"app": "nikke.exe",
					"title": "Goddess of Victory: Nikke"
				},
				{
					"app": "X6Game-Win64-Shipping.exe",
					"title": "Infinity Nikki"
				},
				{
					"app": "GF2_Exilium.exe",
					"title": "GF2 Exilium"
				}
			],
		},
	];

	// Default apps
	let list: App[] = $state(presets[0]["preset"]);
	
	let appUsageDataReq: Promise<AppUsageData[] | null> | null = $state(null);
	let appListReq: Promise<App[] | null> | null = $state(null);

	// svelte-ignore state_referenced_locally
	appUsageDataReq = fetchAppUsageData(list);
	appListReq = fetchAppList();

	// TODO: think of a way to check what apps data already fetched
	// After selection - delete not selected, keep what i have, fetch new
	function getData() { appUsageDataReq = fetchAppUsageData(list); }
	function clearSelecteAppsList() { list = []; }
	const removeSelected = (app: App) => { list = list.filter((f) => f.title !== app.title); };
	const selectPreset = (apps: App[]) => { list = apps; };
</script> 


<!-- TODO:
check calc duration on heatmap for multiple lines. 
	on day 24-07-06 for preset 'gacha', duration is 26.5 hours
also on gacha preset there is line that goes acros the bottom of the chart

add legend to line chart to disable some lines
	add button to disable/enable ALL lines
-->

<!-- Container -->
<div class="flex flex-col gap-4 mt-4">
	<h1 class=" text-[--primary-text] text-3xl font-bold">App Usage Analytics</h1>

	<!-- Controls -->
	<div class="surface flex flex-col gap-4 p-6">

		<!-- Presets -->
		<div class="flex gap-2 border-[--border] border-b border-solid pb-4">
			<div class="pr-2 border-r border-solid border-[--border]"><button class="button" onclick={clearSelecteAppsList}>Clear Data</button></div>
			{#each presets as preset, index}
				<button class="button" onclick={() => selectPreset(preset["preset"])}>{preset["name"]}</button>
			{/each}
		</div>

		<!-- Multiselect -->
		<div class="flex gap-2">
			{#await appListReq}
				<div class="flex justify-center w-full items-center text-1xl p-2">
					<p class="loading">Loading app list...</p>
				</div>
			{:then app_list}
				<button class="button" onclick={getData}>Get Data</button>
				<div class="preview grow relative">
					<MultiSelect {app_list} bind:selectedApps={list}/>
				</div>
			
			{:catch error}
				<p class="error">{error.message}</p>
			{/await}
		</div>

		<!-- Chips -->
		<div class="flex flex-wrap gap-2">
			{#each list as app}
				<Chip {app} onRemove={() => removeSelected(app)} />
			{/each}
		</div>
	</div>

	<!-- Charts -->
	<div class="surface">
		{#await appUsageDataReq}
			<div class="flex justify-center items-center text-4xl p-6">
				<p class="loading">Loading app data...</p>
			</div>
		{:then data} 
			
			{#await appListReq}
				<div class="flex justify-center items-center text-4xl p-6">
					<p class="loading">Loading app list...</p>
				</div>
			{:then app_list} 
				<LineChart {data} {app_list} />
				<HeatmapCalender {data} />
			{:catch error}
				<p class="error">{error.message}</p>
			{/await}
			
		{:catch error}
			<p class="error">{error.message}</p>
		{/await}
	</div>

</div> 

<style>
</style>
