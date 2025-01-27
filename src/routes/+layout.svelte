<script lang="ts">
	import Header from '$lib/Header.svelte';
	import Footer from '$lib/Footer.svelte';
	import '../app.css';
	
	let { children } = $props();
</script>


<!-- TODO: revise tailwind classes, padding and margins especially-->
<div class="flex flex-col min-h-screen">
	<Header />

	<main class="flex-1 flex mx-auto w-full flex-col p-4 max-w-7xl">
		{@render children()}
	</main>

	<Footer />
</div>



<style>
	/* main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 64rem;
		margin: 0 auto;
		box-sizing: border-box;
	} */
</style>
