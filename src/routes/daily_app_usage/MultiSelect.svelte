<!-- <script lang="ts">
    import { type App } from './load';
    let { app_list, selectedApps = $bindable() }: { app_list: App[] | null; selectedApps: App[] } = $props();
    let searchTerm: string = $state('');
    let isDropdownOpen: boolean = $state(false);

    const toggleSelect = (app: App) => {
        if (selectedApps.some(item => item.title === app.title)) {
            selectedApps = selectedApps.filter((f) => f.title !== app.title);
        } else {
            selectedApps = [...selectedApps, app];
        }
    };

    const filteredApps = () => {
        return app_list!.filter((app) =>
            app.title.toLowerCase().includes(searchTerm.toLowerCase())
        );
    };
</script>

<div class="relative w-full">
    <div class="space-y-2">
        <div class="relative">
            <input
                type="text"
                placeholder="Select apps"
                bind:value={searchTerm}
                onfocus={() => isDropdownOpen = true}
                oninput={() => isDropdownOpen = true}
                
                class="w-full rounded-md border border-gray-300 p-2 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />

            {#if isDropdownOpen}
                <ul 
                    class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                    onmouseleave={() => {
                        if (searchTerm === '') isDropdownOpen = false;
                    }}
                >
                    {#if filteredApps().length === 0}
                        <li class="px-4 py-2 text-center text-sm text-gray-500">No results found</li>
                    {:else}
                        {#each filteredApps() as app}
                            <li
                                class="
                                    cursor-pointer 
                                    px-4 py-2 
                                    hover:bg-gray-100 
                                    {selectedApps.some(selected => selected.title === app.title) 
                                        ? 'bg-indigo-100 text-indigo-900' 
                                        : 'text-gray-900'}
                                "
                                onclick={() => {
                                    toggleSelect(app);
                                    if (filteredApps().length === 1) isDropdownOpen = false;
                                }}
                            >
                                {app.title}
                            </li>
                        {/each}
                    {/if}
                </ul>
            {/if}
        </div>
    </div>
</div>

<style>

</style> -->


<script lang="ts">
    import { type App } from './load';
    let { app_list, selectedApps = $bindable() }: { app_list: App[] | null; selectedApps: App[] } = $props();
    let searchTerm: string = $state('');
    let isDropdownOpen: boolean = $state(false);
    let highlightedIndex: number = $state(-1);
    let listRef: HTMLUListElement | null = $state(null);

    const toggleSelect = (app: App) => {
        if (selectedApps.some(item => item.title === app.title)) {
            selectedApps = selectedApps.filter((f) => f.title !== app.title);
        } else {
            selectedApps = [...selectedApps, app];
        }
        console.log(selectedApps);
    };

    const filteredApps = () => {
        return app_list!.filter((app) =>
            app.title.toLowerCase().includes(searchTerm.toLowerCase())
        );
    };

    const handleKeyDown = (e: KeyboardEvent) => {
        const apps = filteredApps();
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                highlightedIndex = highlightedIndex < apps.length - 1 
                    ? highlightedIndex + 1 
                    : 0;
                scrollToHighlighted();
                break;
            
            case 'ArrowUp':
                e.preventDefault();
                highlightedIndex = highlightedIndex > 0 
                    ? highlightedIndex - 1 
                    : apps.length - 1;
                scrollToHighlighted();
                break;
            
            case 'Enter':
                if (highlightedIndex >= 0 && apps[highlightedIndex]) {
                    toggleSelect(apps[highlightedIndex]);
                    if (apps.length === 1) isDropdownOpen = false;
                }
                break;
            
            case 'Escape':
                isDropdownOpen = false;
                break;
        }
    };

    const scrollToHighlighted = () => {
        if (listRef && listRef.children[highlightedIndex]) {
            const highlightedElement = listRef.children[highlightedIndex] as HTMLElement;
            highlightedElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }
    };
</script>

<input
    type="text"
    placeholder="Select apps"
    bind:value={searchTerm}
    onfocus={() => isDropdownOpen = true}
    oninput={() => {
        isDropdownOpen = true;
        highlightedIndex = -1;
    }}
    onkeydown={handleKeyDown}
    class="input"
/>
{#if isDropdownOpen}
    <ul
        bind:this={listRef}
        class="absolute z-10 mt-1 max-h-60 w-64 overflow-auto rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
        onmouseleave={() => {
            if (searchTerm === '') isDropdownOpen = false;
        }}
    >
        {#if filteredApps().length === 0}
            <li class="px-4 py-2 text-center text-sm text-gray-500">No results found</li>
        {:else}
            {#each filteredApps() as app, index}
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
                <li
                    class="
                        cursor-pointer 
                        px-4 py-2 
                        hover:bg-gray-100 
                        {index === highlightedIndex ? 'bg-gray-200' : ''}
                        {selectedApps.some(selected => selected.title === app.title) 
                            ? 'bg-indigo-100 text-indigo-900' 
                            : 'text-gray-900'}
                    "
                    onclick={() => {
                        toggleSelect(app);
                        if (filteredApps().length === 1) isDropdownOpen = false;
                    }}
                >
                    {app.title}
                </li>
            {/each}
        {/if}
    </ul>
{/if}

