<script lang="ts">
	import { 
        fetchAppList, 
        fetchAppUsageData, 
        type App,
        type AppUsageData, 
    } from './load';
	import D3Chart from "./D3Chart.svelte";
	import HeatmapCalender from "./HeatmapCalender.svelte";
	import MultiSelect from "./MultiSelect.svelte";
    import Chip from './Chip.svelte';

	// Presets
	const preset_hoyo: App[] = [
		{ app: 'GenshinImpact.exe', title: 'Genshin Impact' },
		{ app: 'StarRail.exe', title: 'Honkai Star Rail' },
		{ app: 'ZenlessZoneZero.exe', title: 'ZenlessZoneZero' }
	];
	const preset_gacha: App[] = [
			{
				"app": "GenshinImpact.exe",
				"title": "Genshin Impact"
			},
			{
				"app": "StarRail.exe",
				"title": "Honkai Star Rail"
			},
			{
				"app": "ZenlessZoneZero.exe",
				"title": "ZenlessZoneZero"
			},
			{
				"app": "StarRail.exe",
				"title": "Honkai: Star Rail"
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
				"app": "ZenlessZoneZero.exe",
				"title": "Zenless Zone Zero"
			},
			{
				"app": "X6Game-Win64-Shipping.exe",
				"title": "Infinity Nikki"
			},
			{
				"app": "GF2_Exilium.exe",
				"title": "GF2 Exilium"
			}
	];

	// Default apps
	const app1: App = { app: 'GenshinImpact.exe', title: 'Genshin Impact' };
	const app2: App = { app: 'StarRail.exe', title: 'Honkai Star Rail' };
	const app3: App = { app: 'ZenlessZoneZero.exe', title: 'ZenlessZoneZero' };
	let list: App[] = $state([app1, app2, app3]);
	
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
	
	
	
	// Tab Logic
    // const tabTriggers = document.querySelectorAll('.tab-trigger');
    // const tabContents = document.querySelectorAll('.tab-content');

    // tabTriggers.forEach(trigger => {
    //   trigger.addEventListener('click', () => {
    //     const target = trigger.getAttribute('data-target');

    //     // Remove active class from all triggers and contents
    //     tabTriggers.forEach(t => t.classList.remove('active'));
    //     tabContents.forEach(c => c.classList.remove('active'));

    //     // Add active class to the clicked trigger and corresponding content
    //     trigger.classList.add('active');
    //     document.getElementById(target).classList.add('active');
    //   });
    // });


</script> 


<!-- TODO:
on chart titles on tooltip instead of exe

check calc duration on heatmap for multiple lines. 
	on day 24-07-06 for preset 'gacha', duration is 26.5 hours

heatmap tooltip doesn't move with page scroll, it has position absolute
add legend to line chart to disable some lines
	add button to disable/enable ALL lines
-->

<div class="flex flex-col gap-4 p-6">
	<h1 class="text-3xl font-bold text-[--secondary]">App Usage Analytics</h1>

	<!-- Controls -->
	<div class="preview-container">
		<!-- Presets -->
		<div class="flex gap-2">
			<button class="button" onclick={() => selectPreset(preset_hoyo)}>Gi/HSR/ZZZ</button>
			<button class="button" onclick={() => selectPreset(preset_gacha)}>Gacha</button>
		</div>
		<div class="border-b border-solid border-[--border] pb-4"></div>
		<!-- Multiselect -->
		<div class="flex gap-2 pt-4">
			{#await appListReq}
				<p class="loading">Loading app list...</p>
			{:then app_list}
				<div class="preview grow relative">
					<MultiSelect {app_list} bind:selectedApps={list}/>
				</div>
			
				<div class="">
					<button class="button" onclick={getData}>Get Data</button>
					<button class="button" onclick={clearSelecteAppsList}>Clear Data</button>
				</div>
			{:catch error}
				<p class="error">{error.message}</p>
			{/await}
		</div>
		<!-- Chips -->
		<div class="flex flex-wrap gap-2 mx-2 my-1">
			{#each list as app}
				<Chip {app} onRemove={() => removeSelected(app)} />
			{/each}
		</div>
	</div>

	<!-- Charts -->
	<div class="preview-container">
		{#await appUsageDataReq}
			<p class="loading">Loading data...</p>
		{:then data} 
			<D3Chart {data} />
			<HeatmapCalender {data} />
		{:catch error}
			<p class="error">{error.message}</p>
		{/await}
	</div>

</div> 


<style>
	/* Tabs Container */
    .tabs {
      width: 100%;
      font-family: Arial, sans-serif;
    }

    /* Tab List */
    .tab-list {
      display: flex;
      background-color: #4A3B32;
      border: 1px solid #8B6D5C;
      border-radius: 4px 4px 0 0;
    }

    /* Tab Buttons */
    .tab-trigger {
      flex: 1;
      padding: 10px;
      text-align: center;
      cursor: pointer;
      color: #CEB8A2;
      background-color: transparent;
      border: none;
      transition: background-color 0.3s, color 0.3s;
    }

    .tab-trigger.active {
      background-color: #8B6D5C;
      color: #E6D5C3;
    }

    .tab-trigger:hover {
      background-color: #8B6D5C;
      color: #E6D5C3;
    }

    /* Tab Content */
    .tab-content {
      display: none;
      padding: 16px 0;
    }

    .tab-content.active {
      display: block;
    }

    /* Placeholder Styles */
    .placeholder {
      width: 100%;
      height: 400px;
      background-color: #4A3B32;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #CEB8A2;
    }
</style>

