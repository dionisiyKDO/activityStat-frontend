<script>
	import Header from "../Header.svelte";
	import Table from "../Table.svelte";
	import D3Chart from "../D3Chart.svelte";
	import { onMount } from "svelte";


	// @ts-ignore
	let data = $state([]);
    let waiting = $state('Loading...');

    async function getTableItems() {
        const response = await fetch("/api/spent_time");
        const r = JSON.parse( 
            await response.json(), // returns a promise
            // @ts-ignore
            // @ts-ignore
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

<Header />
<main>
    <h1>HAHA</h1>
	{#if data.length > 0}
		<D3Chart {data} />
		<Table {data} {waiting} />
	{/if}
</main>
