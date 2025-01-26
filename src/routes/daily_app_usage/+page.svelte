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

	const app1: App = { app: 'GenshinImpact.exe', title: 'Genshin Impact' };
	const app2: App = { app: 'StarRail.exe', title: 'Honkai Star Rail' };
	const app3: App = { app: 'ZenlessZoneZero.exe', title: 'ZenlessZoneZero' };
	let list: App[] = $state([app1, app2, app3]);
	
	let appListReq: Promise<App[] | null> | null = $state(null);
	let appUsageDataReq: Promise<AppUsageData[] | null> | null = $state(null);

	appListReq = fetchAppList();
	appUsageDataReq = fetchAppUsageData(list);

	// TODO: think of a way to check what apps data already fetched
	// After selection - delete not selected, keep what i have, fetch new
	function getData() {
		appUsageDataReq = fetchAppUsageData(list);
	}

	function clearSelecteAppsList() {
		list = [];
	}
</script> 


<!-- //  let app: string = $state("zen.exe"); -->
<!-- <div class="flex flex-col mb-2">
	<input class="p-1 rounded-lg text-xl" id="app" type="text" bind:value={app} onfocusout={getData} />
</div> -->


{#await appListReq}
	<p class="loading">Loading app list...</p>
{:then app_list}
	<div class="flex justify-center">
		<div class="flex gap-4">
			<button class="w-40" onclick={getData}>Clear Data</button>
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
