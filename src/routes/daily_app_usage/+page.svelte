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

	const app1: App = { app: 'GenshinImpact.exe', title: 'Genshin Impact' };
	const app2: App = { app: 'StarRail.exe', title: 'Honkai Star Rail' };
	const app3: App = { app: 'ZenlessZoneZero.exe', title: 'ZenlessZoneZero' };
	let list: App[] = $state([app1, app2, app3]);
	
	let appListReq: Promise<App[] | null> | null = $state(null);
	let appUsageDataReq: Promise<AppUsageData[] | null> | null = $state(null);

	appListReq = fetchAppList();
	// svelte-ignore state_referenced_locally
	appUsageDataReq = fetchAppUsageData(list);

	// TODO: think of a way to check what apps data already fetched
	// After selection - delete not selected, keep what i have, fetch new
	function getData() {
		appUsageDataReq = fetchAppUsageData(list);
	}

	function clearSelecteAppsList() {
		list = [];
	}

	const removeSelected = (app: App) => {
		list = list.filter((f) => f.title !== app.title);
	};
</script> 


<!-- 
show selected apps somewhere
preset buttons for bundle of apps
on chart titles on tooltip instead of exe

heatmap tooltip doesn't move with page scroll, it has position absolute
-->


{#await appListReq}
	<p class="loading">Loading app list...</p>
{:then app_list}
	<!-- Chips -->
	<div class="flex flex-wrap justify-center gap-2 mb-2">
		{#each list as app}
			<Chip {app} onRemove={() => removeSelected(app)} />
		{/each}
	</div>

	<!-- Multiselect -->
	<div class="flex justify-center">
		<div class="flex gap-4">
			<button class="w-40" onclick={clearSelecteAppsList}>Clear Data</button>
			<MultiSelect {app_list} bind:selectedApps={list}/>
			<button class="w-40" onclick={getData}>Get Data</button>
		</div>
	</div>
{:catch error}
	<p class="error">{error.message}</p>
{/await}


{#await appUsageDataReq}
	<p class="loading">Loading data...</p>
{:then data} 
	<D3Chart {data} />
	<HeatmapCalender {data} />

{:catch error}
	<p class="error">{error.message}</p>
{/await}















<!-- for comment's replace '- -' to '--' -->
<!-- <div class="flex flex-col gap-4 p-4">
	<h1 class="text-3xl font-bold text-[#E6D5C3]">App Usage Analytics</h1>

	<div class="preview-container">
		<!- - Presets - ->
		<div class="preview">Presets</div>
		<hr class="border-solid border-[- -muted] border-t-0 border-b-2" />
		<!- - Multiselect - ->
		<div class="flex gap-2">
			<div class="preview grow">Multiselect</div>
			<div class="">
				<button class="preview">Get Data</button>
				<button class="preview">Clear Data</button>
			</div>
		</div>
		<!- - Chips - ->
		<div class="flex gap-2">
			<div class="preview-chip">Chip1 X</div>
			<div class="preview-chip">Chip2 X</div>
			<div class="preview-chip">Chip3 X</div>
			<div class="preview-chip">Chip4 X</div>
			<div class="preview-chip">Chip5 X</div>
		</div>
	</div>

	<div class="preview-container">
		<div class="tabs">
			<!- - Tab List - ->
			<div class="tab-list">
				<button class="tab-trigger active" data-target="line">Line Graph</button>
				<button class="tab-trigger" data-target="heatmap">Heatmap</button>
			</div>
		
			<!- - Tab Content - ->
			<div id="line" class="tab-content active">
			  	<div class="placeholder">Line Chart Placeholder</div>
			</div>
		
			<div id="heatmap" class="tab-content">
			  	<div class="placeholder">Heatmap Placeholder</div>
			</div>
		</div>
	</div>

</div> 


<script>
	// Tab Logic
    const tabTriggers = document.querySelectorAll('.tab-trigger');
    const tabContents = document.querySelectorAll('.tab-content');

    tabTriggers.forEach(trigger => {
      trigger.addEventListener('click', () => {
        const target = trigger.getAttribute('data-target');

        // Remove active class from all triggers and contents
        tabTriggers.forEach(t => t.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));

        // Add active class to the clicked trigger and corresponding content
        trigger.classList.add('active');
        document.getElementById(target).classList.add('active');
      });
    });
</script>


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

-->
