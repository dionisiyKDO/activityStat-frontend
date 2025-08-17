import { type AppUsageData, type App, type OSUsageData } from '$lib/types';

export async function fetchAppOSData(): Promise<OSUsageData[] | null> {
	try {
		const response = await fetch(`/api/daily_os_usage/`);

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch os';
			console.log(error);
			return null;
		}

		let data: OSUsageData[] = await response.json();
		data = data.map((d: any) => {
			return {
				date: new Date(d.date),
				platform: d.platform,
				duration: d.duration
			};
		});
		// console.log(data);
		// const osNames: string[] = Array.from(new Set(data.map((d) => d.app)));
		// // make similar to App type to reuse LineChart component
		// const osData: { app: string[]; title: string }[] = osNames.map((os) => {
		// 	return {
		// 		app: [os],
		// 		title: os
		// 	};
		// });

		return data;
	} catch (err) {
		console.log(err);
		return null;
	}
}
