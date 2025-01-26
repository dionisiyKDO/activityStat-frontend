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

	
	let appListReq: Promise<App[] | null> | null = $state(null);
	let appUsageDataReq: Promise<AppUsageData[] | null> | null = $state(null);

	let app: string = $state("zen.exe");

	appListReq = fetchAppList();
	appUsageDataReq = fetchAppUsageData(app);

	function getData() {
		appUsageDataReq = fetchAppUsageData(app);
	}

	let list: App[] = $state([]);
	$inspect(list);
</script> 


<!-- <div class="flex flex-col mb-2">
	<input class="p-1 rounded-lg text-xl" id="app" type="text" bind:value={app} onfocusout={getData} />
</div> -->


{#await appListReq}
	<p class="loading">Loading app list...</p>
{:then app_list}
	<div class="flex gap-2">
		{#each list as app}
			{app.title}
		{/each}
	</div>
	<div class="flex justify-center">
		<div class="flex gap-4">
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
