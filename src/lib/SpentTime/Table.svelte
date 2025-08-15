<!-- lib/SpentTime/Table.svelte -->
<script lang="ts">
	import { type SpentTime } from '../../routes/spent_time/load';
	let { data }: { data: SpentTime[] } = $props();
</script>

<div class="h-full rounded flex flex-col">
	<div class="flex flex-col flex-1 overflow-hidden">
		<table class="w-full border-collapse flex flex-col h-full">
			
			<thead class="bg-[--secondary] text-[--secondary-text] rounded-t-lg flex-shrink-0 sticky top-0 z-10">
				<tr class="flex pr-2">
					<th class="p-2.5 text-left border-r border-[--border] border-solid flex-1">App</th>
					<th class="p-2.5 text-left w-20 flex-shrink-0">Hours</th>
				</tr>
			</thead>
			
			<tbody class="flex-1 overflow-y-auto pr-2">
				{#each data as entry}
					<tr class="flex">
						<td class="p-2.5 truncate flex-1 border-r border-[--border] border-solid  min-w-0">{entry.title || entry.app}</td>
						<td class="p-2.5 w-20 flex-shrink-0 text-right">{entry.duration}</td>
					</tr>
				{/each}
			</tbody>
			
		</table>
	</div>
</div>