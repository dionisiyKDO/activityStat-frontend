<script lang="ts">
	import { 
        fetchSpentTime, 
        fetchMetadata, 
        type SpentTime, 
        type Metadata 
    } from './load';

	import D3Chart from './D3Chart.svelte';
	import Table from './Table.svelte';
	import { onMount } from 'svelte';

	let trackStatsReq: Promise<SpentTime[] | null>;
	let metadataReq: Promise<Metadata | null>;

	onMount(() => {
		trackStatsReq = fetchSpentTime();
		metadataReq = fetchMetadata();
	});
</script>

{#await trackStatsReq}
	<p class="loading">Loading list...</p>
{:then data}
	{#if data != null}
        {#await metadataReq}
            <p class="loading">Loading metadata...</p>
        {:then metadata}
        
            <div class="flex gap-4 m-4">
                <h1>Spent Time</h1>
                {#if metadata != null}
                    <p class="">Start date: {metadata.start_date}</p>
                    <p class="">End date: {metadata.end_date}</p>
                    <p class="">Total records: {metadata.total_records}</p>
                {/if}
            </div>

            <D3Chart {data} />
            <Table {data} />
        {:catch error}
            <p class="error">{error.message}</p>
        {/await}
    {/if}
{:catch error}
	<p class="error">{error.message}</p>
{/await}


<style>
</style>
