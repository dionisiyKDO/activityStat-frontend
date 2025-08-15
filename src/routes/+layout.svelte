<!-- routes/+layout.svelte -->
<script lang="ts">
	import Header from '$lib/Header.svelte';
	import Footer from '$lib/Footer.svelte';
	import '../app.css';
	
	let { children } = $props();
</script>

<div class="min-h-screen flex flex-col">
	<Header />

	<main class="flex-1 container mx-auto p-4 relative">
		{@render children()}
	</main>

	<Footer />
</div>
