import { type RawAppUsageData, type AppUsageData, type App } from '$lib/types';

export async function fetchAppUsageData(apps: App[]): Promise<AppUsageData[] | null> {
	try {
		if (apps.length === 0) return [];

		const response = await fetch(`/api/daily_app_usage`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				app_titles: apps.map(app => app.title)
			})
		});

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch app';
			console.log(error);
			return null;
		}

		const raw_data: RawAppUsageData[] = await response.json();
		let data: AppUsageData[] = raw_data.map((d: any) => {
			return {
				timestamp: d.date,
				date: new Date(d.date),
				app: d.app,
				duration: d.duration
			};
		});

		return data;
	} catch (err) {
		console.log(err);
		return null;
	}
}

export async function fetchAppList(): Promise<App[] | null> {
	try {
		const response = await fetch(`/api/app_list/`);

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch app list';
			console.log(error);
			return null;
		}

		const data: Record<string, string[]> = await response.json();

		const appList: App[] = Object.entries(data).map(([title, executables]) => ({
			title: title,
			app: executables
		}));

		return appList;
	} catch (err) {
		console.log(err);
		return null;
	}
}
