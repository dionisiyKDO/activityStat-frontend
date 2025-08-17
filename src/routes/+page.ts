// routes/+page.js
import { redirect } from '@sveltejs/kit';

export function load() {
	throw redirect(308, '/spent_time');
}
