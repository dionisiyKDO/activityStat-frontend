<script>
    export let data;
    export let waiting;
</script>

<div class="container">
    <p>{waiting}</p>
    {#if !waiting}
        <table>
            <thead>
                <tr>
                    <th>App Name</th>
                    <th>Duration (hours)</th>
                </tr>
            </thead>
            <tbody>
                {#each data as entrie}
                    <tr>
                        {#if (entrie.title) }
                            <td>{entrie.title}</td>
                        {:else}
                            <td>{entrie.app}</td>
                        {/if}
                        <td>{entrie.duration}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    {/if}
</div>

<style>
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 18px;
        text-align: left;
    }

    th, td {
        padding: 12px;
        border-bottom: 1px solid #a5a5a5;
    }

    th {
        background-color: #f2f2f2;
        color: black;
    }

    tr:hover {
        background-color: #353535;
        color: #f2f2f2;
    }
</style>