<script lang="ts">
	import type { App } from '$lib/types';

	let { app, onRemove }: { app: App; onRemove: () => void } = $props();
</script>

<div class="chip">
	{app.title}
	<button onclick={onRemove} class="chip-button">&times;</button>
</div>
