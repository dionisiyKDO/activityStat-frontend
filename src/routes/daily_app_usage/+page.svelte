<!-- routes/daily_app_usage/+page.svelte -->
<script lang="ts">
	import HeatmapCalender from '$lib/AppUsageTime/HeatmapCalender.svelte';
	import MultiSelect from '$lib/AppUsageTime/MultiSelect.svelte';
	import LineChart from '$lib/AppUsageTime/LineChart.svelte';
	import Chip from '$lib/AppUsageTime/Chip.svelte';
	import { fetchAppList, fetchAppUsageData } from './load';
	import { type App, type AppUsageData } from '$lib/types';

	// Presets
	const presets = [
		{
			name: 'Gi/HSR/ZZZ',
			preset: [
				{ app: ['GenshinImpact.exe'], title: 'Genshin Impact' },
				{ app: ['StarRail.exe'], title: 'Honkai: Star Rail' },
				{ app: ['ZenlessZoneZero.exe'], title: 'Zenless Zone Zero' }
			]
		},
		{
			name: 'Gacha',
			preset: [
				{
					app: ['GenshinImpact.exe'],
					title: 'Genshin Impact'
				},
				{
					app: ['StarRail.exe'],
					title: 'Honkai: Star Rail'
				},
				{
					app: ['ZenlessZoneZero.exe'],
					title: 'Zenless Zone Zero'
				},
				{
					app: ['BlueArchive.exe'],
					title: 'Blue Archive'
				},
				{
					app: ['Client-Win64-Shipping.exe'],
					title: 'Wuthering Waves'
				},
				{
					app: ['dnplayer.exe'],
					title: 'LDPlayer'
				},
				{
					app: ['reverse1999.exe'],
					title: 'Reverse 1999'
				},
				{
					app: ['nikke.exe'],
					title: 'Goddess of Victory: Nikke'
				},
				{
					app: ['X6Game-Win64-Shipping.exe'],
					title: 'Infinity Nikki'
				},
				{
					app: ['GF2_Exilium.exe'],
					title: 'GF2 Exilium'
				}
			]
		}
	];

	// Default apps
	let list: App[] = $state(presets[0]['preset']);

	let appUsageDataReq: Promise<AppUsageData[] | null> | null = $state(null);
	let appListReq: Promise<App[] | null> | null = $state(null);

	appUsageDataReq = fetchAppUsageData(presets[0]['preset']);
	appListReq = fetchAppList();

	function getData() {
		appUsageDataReq = fetchAppUsageData(list);
	}
	function clearSelecteAppsList() {
		list = [];
	}
	const removeSelected = (app: App) => {
		list = list.filter((f) => f.title !== app.title);
	};
	const selectPreset = (apps: App[]) => {
		list = apps;
	};
</script>

<!-- Container -->
<div class="mt-4 flex flex-col gap-4">
	<h1 class="text-3xl font-bold text-[--primary-text]">App Usage Analytics</h1>

	<!-- Controls -->
	<div class="surface flex flex-col gap-4 p-6">
		<!-- Presets -->
		<div class="flex gap-2 border-b border-solid border-[--border] pb-4">
			<div class="border-r border-solid border-[--border] pr-2">
				<button class="button" onclick={clearSelecteAppsList}>Clear Data</button>
			</div>
			{#each presets as preset, index}
				<button class="button" onclick={() => selectPreset(preset['preset'])}
					>{preset['name']}</button
				>
			{/each}
		</div>

		<!-- Multiselect -->
		<div class="flex gap-2">
			{#await appListReq}
				<div class="text-1xl flex w-full items-center justify-center p-2">
					<p class="loading">Loading app list...</p>
				</div>
			{:then app_list}
				<button class="button" onclick={getData}>Get Data</button>
				<div class="preview relative grow">
					<MultiSelect {app_list} bind:selectedApps={list} />
				</div>
			{:catch error}
				<p class="error">{error.message}</p>
			{/await}
		</div>

		<!-- Chips -->
		<div class="flex flex-wrap gap-2">
			{#each list as app}
				<Chip {app} onRemove={() => removeSelected(app)} />
			{/each}
		</div>
	</div>

	<!-- Charts -->
	<div class="surface">
		{#await appUsageDataReq}
			<div class="flex items-center justify-center p-6 text-4xl">
				<p class="loading">Loading app data...</p>
			</div>
		{:then data}
			{#await appListReq}
				<div class="flex items-center justify-center p-6 text-4xl">
					<p class="loading">Loading app list...</p>
				</div>
			{:then app_list}
				<LineChart {data} {app_list} />
				<HeatmapCalender {data} />
			{:catch error}
				<p class="error">{error.message}</p>
			{/await}
		{:catch error}
			<p class="error">{error.message}</p>
		{/await}
	</div>
</div>
