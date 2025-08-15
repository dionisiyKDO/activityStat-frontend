<script lang="ts">
    import type { App } from "../../routes/daily_app_usage/load";

    export let app: App;
    export let onRemove: () => void;
</script>

<div class="chip">
    {app.title}
    <button onclick={onRemove} class="chip-button">&times;</button>
</div>

