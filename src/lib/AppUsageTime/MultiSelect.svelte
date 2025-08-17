<script lang="ts">
	import { type App } from '$lib/types';

	interface Props {
		app_list: App[] | null;
		selectedApps: App[];
	}
	let { app_list, selectedApps = $bindable() }: Props = $props();

	let searchTerm: string = $state('');
	let isDropdownOpen: boolean = $state(false);
	let highlightedIndex: number = $state(-1);
	let dropdownRef: HTMLElement | null = $state(null);

	// Create a Set for O(1) lookup of selected apps
	const selectedTitles = $derived(new Set(selectedApps.map((app) => app.title)));

	const toggleSelect = (app: App) => {
		if (selectedTitles.has(app.title)) {
			selectedApps = selectedApps.filter((f) => f.title !== app.title);
		} else {
			selectedApps = [...selectedApps, app];
		}
	};

	const filteredApps = $derived.by(() => {
		if (!app_list) return [];

		const lowerSearchTerm = searchTerm.toLowerCase();
		if (!lowerSearchTerm) {
			return app_list;
		}

		return app_list.filter((app) => app.title.toLowerCase().includes(lowerSearchTerm));
	});

	// Reset highlighted index when filtered apps change
	$effect(() => {
		if (filteredApps.length === 0) {
			highlightedIndex = -1;
		} else if (highlightedIndex >= filteredApps.length) {
			highlightedIndex = Math.max(0, filteredApps.length - 1);
		}
	});

	const handleKeyDown = (e: KeyboardEvent) => {
		const apps = filteredApps;

		switch (e.key) {
			case 'ArrowDown':
				e.preventDefault();
				highlightedIndex = (highlightedIndex + 1) % apps.length;
				scrollToHighlighted();
				break;

			case 'ArrowUp':
				e.preventDefault();
				highlightedIndex = (highlightedIndex - 1 + apps.length) % apps.length;
				scrollToHighlighted();
				break;

			case 'Enter':
				if (highlightedIndex >= 0 && apps[highlightedIndex]) {
					toggleSelect(apps[highlightedIndex]);
					// if (apps.length === 1) isDropdownOpen = false;
					isDropdownOpen = false;
					searchTerm = '';
				}
				break;

			case 'Escape':
				isDropdownOpen = false;
				break;
		}
	};

	function clickOutside(node: HTMLElement) {
		const handleClick = (event: MouseEvent) => {
			const target = event.target as Node;
			if (node && !node.contains(target) && !dropdownRef?.contains(target)) {
				isDropdownOpen = false;
			}
		};

		document.addEventListener('click', handleClick, true);
		return {
			destroy() {
				document.removeEventListener('click', handleClick, true);
			}
		};
	}

	const scrollToHighlighted = () => {
		if (dropdownRef?.children[highlightedIndex]) {
			const highlightedElement = dropdownRef.children[highlightedIndex] as HTMLElement;
			highlightedElement.scrollIntoView({
				behavior: 'instant',
				block: 'nearest'
			});
		}
	};

	// Handle input focus and changes
	const handleFocus = () => {
		isDropdownOpen = true;
	};

	const handleInput = () => {
		isDropdownOpen = true;
		highlightedIndex = filteredApps.length > 0 ? 0 : -1;
	};

	const handleItemClick = (app: App) => {
		toggleSelect(app);
		isDropdownOpen = false;
	};

	const handleMouseOver = (index: number) => {
		highlightedIndex = index;
	};
</script>

<input
	type="text"
	placeholder="Select apps"
	bind:value={searchTerm}
	onfocus={handleFocus}
	oninput={handleInput}
	onkeydown={handleKeyDown}
	use:clickOutside
	class="input w-full"
/>
{#if isDropdownOpen}
	<ul
		bind:this={dropdownRef}
		class="
        absolute z-10
        mt-1
        max-h-60
        w-60
        overflow-y-auto
        rounded-lg bg-[--muted-background]
        text-[--foreground]
        shadow-lg
        "
	>
		{#if filteredApps.length === 0}
			<li class="px-4 py-2 text-center text-sm text-gray-500">No results found</li>
		{:else}
			{#each filteredApps as app, index (app.title)}
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
				<li
					class="
                        cursor-pointer
                        px-4 py-2
                        hover:bg-[--input-background]
                        {index === highlightedIndex ? 'bg-[--input-background]' : ''}
                        {selectedTitles.has(app.title) ? 'text-[--primary]' : 'text-[--foreground]'}
                    "
					onclick={() => handleItemClick(app)}
					onmouseover={() => handleMouseOver(index)}
					onfocus={() => handleMouseOver(index)}
				>
					{app.title}
				</li>
			{/each}
		{/if}
	</ul>
{/if}
