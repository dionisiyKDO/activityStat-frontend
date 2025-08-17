<script lang="ts">
	import BarChart from '$lib/SpentTime/BarChart.svelte';
	import Table from '$lib/SpentTime/Table.svelte';
	import { fetchSpentTime, fetchMetadata } from './load';
	import { type SpentTime, type Metadata } from '$lib/types';

	// Requests
	let trackStatsReq: Promise<SpentTime[] | null> = fetchSpentTime();
	let metadataReq: Promise<Metadata | null> = fetchMetadata();
</script>

{#await trackStatsReq}
	<p class="loading">Loading list...</p>
{:then data}
	{#if data}
		<h1 class="mb-4 text-3xl font-bold text-[--primary-text]">Spent Time</h1>

		<!-- Main content area with two columns -->
		<div class="flex gap-4">
			<!-- Left side - 70% width, scrollable content -->
			<div class="w-[70%] flex-shrink-0">
				<div class="surface mb-4 p-4">
					<BarChart data={data.slice(0, 10)} />
				</div>

				<!-- Add more content here - forms, buttons, etc. -->
				{#await metadataReq}
					<p class="loading">Loading metadata...</p>
				{:then metadata}
					<div class="surface">
						{#if metadata != null}
							<div class="m-4 flex gap-4">
								<p class="block rounded-md border border-solid border-[--border] p-2">
									<strong>Start date:</strong>
									{metadata.start_date}
								</p>
								<p class="block rounded-md border border-solid border-[--border] p-2">
									<strong>End date:</strong>
									{metadata.end_date}
								</p>
								<p class="block rounded-md border border-solid border-[--border] p-2">
									<strong>Total records:</strong>
									{metadata.total_records}
								</p>
							</div>
						{/if}
					</div>
				{:catch error}
					<p class="error">{error.message}</p>
				{/await}
			</div>

			<!-- Right side - 30% width, sticky table -->
			<div class="w-[30%] flex-shrink-0">
				<div class="surface sticky top-24 h-[80vh]">
					<Table {data} />
				</div>
			</div>
		</div>
	{/if}
{:catch error}
	<p class="error">{error.message}</p>
{/await}
