<script lang="ts">
    import { type App } from './load';
    let { app_list, selectedApps = $bindable() }: { app_list: App[] | null; selectedApps: App[] } = $props();
    let searchTerm: string = $state('');
    let isDropdownOpen: boolean = $state(false);
    let highlightedIndex: number = $state(-1);
    let dropdownRef: HTMLElement | null = $state(null);

    const toggleSelect = (app: App) => {
        if (selectedApps.some(item => item.title === app.title)) {
            selectedApps = selectedApps.filter((f) => f.title !== app.title);
        } else {
            selectedApps = [...selectedApps, app];
        }
    };

    const filteredApps = (): App[] => {
        if (!app_list) return [];
        return Object.entries(app_list)
            .filter(([title]) => 
                title.toLowerCase().includes(searchTerm.toLowerCase())
            )
            .map(([title, executables]) => ({ "app":  executables, "title": title }));
    };


    const handleKeyDown = (e: KeyboardEvent) => {
        const apps = filteredApps();

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
                if (highlightedIndex >= 0) {
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
            if (node && !node.contains(event.target as Node) && !dropdownRef?.contains(event.target as Node)) {
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
        if (dropdownRef && dropdownRef.children[highlightedIndex]) {
            const highlightedElement = dropdownRef.children[highlightedIndex] as HTMLElement;
            highlightedElement.scrollIntoView({ 
                behavior: 'instant', 
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
        highlightedIndex = 0;
    }}
    onkeydown={handleKeyDown}
    use:clickOutside
    class="input w-full"
/>
{#if isDropdownOpen}
    <ul
        bind:this={dropdownRef}
        class="
        max-h-60 w-60
        mt-1
        absolute
        z-10         
        overflow-y-auto 
        rounded-lg shadow-lg 
        bg-[--muted-background]
        text-[--foreground]
        "
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
                        hover:bg-[--input-background]
                        {index === highlightedIndex ? 'bg-[--input-background]' : ''}
                        {selectedApps.some(selected => selected.title === app.title) 
                            ? 'text-[--primary]' 
                            : 'text-[--foreground]'}
                    "
                    onclick={() => {
                        toggleSelect(app);
                        isDropdownOpen = false;
                    }}
                    onmouseover={() => { highlightedIndex = index; }}
                    onfocus={() => { highlightedIndex = index; }}
                >
                    {app.title}
                </li>
            {/each}
        {/if}
    </ul>
{/if}

