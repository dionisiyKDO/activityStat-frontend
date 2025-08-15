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

{#await trackStatsReq}
	<p class="loading">Loading list...</p>
{:then data}
	{#if data}
        
        <!-- Main content area with two columns -->
        <div class="flex gap-4">
            
            <!-- Left side - 70% width, scrollable content -->
            <div class="w-[70%] flex-shrink-0">
                <div class="p-4 mb-4 surface">
                    <BarChart data={data.slice(0, 17)} />
                </div>

                <!-- Add more content here - forms, buttons, etc. -->
                <!-- <div class="rounded p-4 surface">
                    <h3 class="text-[--primary-text] text-lg mb-2">Additional Content</h3>
                    {#each Array(20).fill(0) as _, i}
                        <div class="p-2 rounded mb-2">
                            <p>Content block {i + 1}</p>
                        </div>
                    {/each}
                </div> -->
            </div>
            
            <!-- Right side - 30% width, sticky table -->
            <div class="w-[30%] flex-shrink-0">
                <div class="sticky top-24 surface h-[80vh]">
                    <Table {data} />
                </div>
            </div>
            
        </div>
        
	{/if}
{:catch error}
	<p class="error">{error.message}</p>
{/await}


<!-- {#await metadataReq}
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
{/await} -->

