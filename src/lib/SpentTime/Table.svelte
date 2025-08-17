<!-- lib/SpentTime/Table.svelte -->
<script lang="ts">
	import { type SpentTime } from '$lib/types';
	let { data }: { data: SpentTime[] } = $props();
</script>

<div class="flex h-full flex-col rounded">
	<div class="flex flex-1 flex-col overflow-hidden">
		<table class="flex h-full w-full border-collapse flex-col">
			<thead
				class="sticky top-0 z-10 flex-shrink-0 rounded-t-lg bg-[--secondary] text-[--secondary-text]"
			>
				<tr class="flex pr-2">
					<th class="flex-1 border-r border-solid border-[--border] p-2.5 text-left">App</th>
					<th class="w-20 flex-shrink-0 p-2.5 text-left">Hours</th>
				</tr>
			</thead>

			<tbody class="flex-1 overflow-y-auto pr-2">
				{#each data as entry}
					<tr class="flex">
						<td class="min-w-0 flex-1 truncate border-r border-solid border-[--border] p-2.5"
							>{entry.title || entry.app}</td
						>
						<td class="w-20 flex-shrink-0 p-2.5 text-right">{entry.duration}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
