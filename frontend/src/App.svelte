<script>
	import Header from "./lib/Header.svelte";
	import Table from "./lib/Table.svelte";
	import { onMount } from "svelte";

	let count = $state(0);

	function increment() {
		count += 1;
	}
</script>

<Header />
<main>
	<button onclick={increment}>
		clicks: {count}
	</button>

	<Table />
</main>
