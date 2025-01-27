<script lang="ts">
    import type { App } from "./load";

    export let app: App;
    export let onRemove: () => void;
</script>

<div class="flex gap-1 h-fit rounded-2xl bg-[--secondary] text-[--secondary-foreground] text-sm p-0 px-3">
    <p class="inline">{app.title}</p>
    <button onclick={onRemove} class="rounded-2xl bg-[--secondary] text-[--secondary-foreground] text-sm p-0 px-2">&times;</button>
</div>

