import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
		  // string shorthand: http://localhost:5173/foo -> http://localhost:4567/foo
		  // '/': 'http://localhost:5173',
	
		  '/api': {
			target: 'http://localhost:8000',
			changeOrigin: true,
			rewrite: (path) => path.replace(/^\/api/, ''),
		  },
		}
	  }
});
