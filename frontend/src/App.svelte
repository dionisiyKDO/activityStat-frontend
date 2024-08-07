<script>
	import Header from "./lib/Header.svelte";
	import Table from "./lib/Table.svelte";
	import D3Chart from "./lib/D3Chart.svelte";
	import { onMount } from "svelte";


	let data = $state([]);
    let waiting = $state('Loading...');

    async function getTableItems() {
        const response = await fetch("/api/items");
        const r = JSON.parse( await response.json() );

        data = r;
        waiting = '';

        console.log(r);
    }

    onMount(() => {
        getTableItems();
    });
</script>

<Header />
<main>
	{#if data.length > 0}
		<D3Chart {data} />
		<Table {data} {waiting} />
	{/if}
</main>
