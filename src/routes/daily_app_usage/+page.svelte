<script lang="ts">
	import { 
        fetchAppList, 
        fetchAppUsageData, 
        type AppList,
        type AppUsageData, 
    } from './load';
	import D3Chart from "./D3Chart.svelte";
	import { onMount } from "svelte";
	
	let appListReq: Promise<AppList[] | null> | null = $state(null);
	let appUsageDataReq: Promise<AppUsageData[] | null> | null = $state(null);

	let app: string = $state("zen.exe");

	appListReq = fetchAppList();
	appUsageDataReq = fetchAppUsageData(app);

	function getData() {
		appUsageDataReq = fetchAppUsageData(app);
	}
</script> 


<div class="flex flex-col mb-2">
	<input class="p-1 rounded-lg text-xl" id="app" type="text" bind:value={app} onfocusout={getData} />
</div>

{#await appUsageDataReq}
	<p class="loading">Loading data...</p>
{:then data} 
	{#await appListReq}
		<p class="loading">Loading app list...</p>
	{:then app_list}


		<D3Chart {data} {app_list} />


	{:catch error}
		<p class="error">{error.message}</p>
	{/await}

{:catch error}
	<p class="error">{error.message}</p>
{/await}
