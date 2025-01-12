<script lang="ts">
	import Header from '$lib/Header.svelte';
	import Footer from '$lib/Footer.svelte';
	import '../app.css';
	
	let { children } = $props();
</script>


<div class="flex flex-col h-screen">
	<Header />

	<main class="flex-1 flex flex-col p-4">
		{@render children()}
	</main>

	<Footer />
</div>



<style>
</style>
