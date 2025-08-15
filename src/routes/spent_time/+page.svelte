<script lang="ts">
	import BarChart from '$lib/SpentTime/BarChart.svelte';
	import Table from '$lib/SpentTime/Table.svelte';
	import { 
        fetchSpentTime, 
        fetchMetadata, 
        type SpentTime, 
        type Metadata 
    } from './load';

    // Requests
	let trackStatsReq: Promise<SpentTime[] | null> = fetchSpentTime();
	let metadataReq: Promise<Metadata | null> = fetchMetadata();
</script>

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
{:catch error}
    <p class="error">{error.message}</p>
{/await}


{#await trackStatsReq}
	<p class="loading">Loading list...</p>
{:then data}
	{#if data != null}
        <BarChart {data} />
        <Table {data} />
    {/if}
{:catch error}
	<p class="error">{error.message}</p>
{/await}
