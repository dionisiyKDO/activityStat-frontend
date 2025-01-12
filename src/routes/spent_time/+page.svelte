<script>
    // @ts-nocheck
	import Header from "$lib/Header.svelte";
	import Table from "$lib/Table.svelte";
	import D3Chart from "./D3Chart.svelte";
	import { onMount } from "svelte";


	let data = $state([]);
    let waiting = $state('Loading...');

    async function getTableItems() {
        const response = await fetch("/api/spent_time");
        const r = JSON.parse( 
            await response.json(), // returns a promise
            (key, value) => typeof value === "number" ? Math.round(value * 100) / 100 : value // rounding
        );

        data = r;
        waiting = '';

        console.log(r);
    }

    onMount(() => {
        getTableItems();
    });
</script> 

<main>
	{#if data.length > 0}
		<D3Chart {data} />
		<Table {data} {waiting} />
	{/if}
</main>
