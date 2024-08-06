<script>
  import { onMount } from 'svelte';
  import axios from 'axios';

  let message = 'Loading...';

  onMount(async () => {
    try {
      const response = await axios.get('/api');
      message = response.data.Hello;
    } catch (error) {
      message = 'Error fetching data';
    }
  });
</script>

<main>
  <h1>Lorem ipsum dolor sit amet consectetur adipisicing elit. Alias aut expedita sed quibusdam, dignissimos placeat suscipit modi iusto quisquam sequi tempora optio nobis laboriosam pariatur autem. Laborum odio assumenda aliquam!</h1>
</main>

<style>
  main {
    text-align: center;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }
  h1 {
    color: #ff3e00;
    text-transform: uppercase;
  }
</style>
