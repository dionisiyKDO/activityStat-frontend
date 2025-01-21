<script lang="ts">
	import Header from '$lib/Header.svelte';
	import Footer from '$lib/Footer.svelte';
	import '../app.css';
	
	let { children } = $props();
</script>


<div class="flex flex-col h-screen">
	<Header />

	<main class="flex-1 flex mx-auto w-full flex-col p-4">
		{@render children()}
	</main>

	<Footer />
</div>



<style>
	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 64rem;
		margin: 0 auto;
		box-sizing: border-box;
	}
</style>
