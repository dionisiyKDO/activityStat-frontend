<script lang="ts">
    import type { App } from "./load";

    export let app: App;
    export let onRemove: () => void;
</script>

<div class="chip">
    {app.title}
    <button onclick={onRemove} class="chip-button">&times;</button>
</div>

