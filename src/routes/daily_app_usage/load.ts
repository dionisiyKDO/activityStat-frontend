export interface AppUsageData {
	timestamp: number
	date: Date | null
	app: string
	duration: number
}

export interface RawAppUsageData {
	date: number
	duration: number
}

export interface App {
	app: string
	title: string
}

export async function fetchAppUsageData(apps: App[]): Promise<AppUsageData[] | null>   {
	try {
		let results: AppUsageData[] = [];
		console.log(apps);
		
		
		for (const app of apps) {
		
			const response = await fetch(
				`/api/daily_app_usage/${app.title}`
			);

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
					app: app.title,
					duration: d.duration,
				}
			});			

			results.push(...data);
		}
		
		return results;
	} catch (err) {
		console.log(err);
		return null;
	}
}


export async function fetchAppList(): Promise<App[] | null>  {
	try {
		const response = await fetch(
			`/api/app_list/`
		);

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch app list';
			console.log(error);
			return null;
		}

		const data: App[] = await response.json();		
		return data;
	} catch (err) {
		console.log(err);
		return null;
	}
}