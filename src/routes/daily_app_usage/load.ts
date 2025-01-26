export interface AppUsageData {
	timestamp: number
	date: Date | null
	app: string
	duration: number
}

export interface margin {
	top: number;
	right: number;
	bottom: number;
	left: number;
};

export async function fetchAppUsageData(app: string): Promise<AppUsageData[] | null>   {
	try {
		const response = await fetch("/api/daily_app_usage/" + app);

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch tracks';
			console.log(error);
			return null;
		}

		const raw_data: AppUsageData[] | any = JSON.parse(await response.json());

		let data: AppUsageData[] = raw_data.map((d: any) => {
			return {
				timestamp: d.timestamp,
				date: new Date(d.timestamp),
				app: d.app,
				duration: Math.round(d.duration * 100) / 100,
			}
		});
		
		return data;
	} catch (err) {
		console.log(err);
		return null;
	}
}


export interface App {
	app: string
	title: string
}
  
export async function fetchAppList(): Promise<App[] | null>  {
	try {
		const response = await fetch("/api/app_list/");

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch tracks';
			console.log(error);
			return null;
		}

		const data = (await response.json());		
		return data;
	} catch (err) {
		console.log(err);
		return null;
	}
}