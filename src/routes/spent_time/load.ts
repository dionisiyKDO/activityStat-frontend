export interface SpentTime {
	app: string;
	duration: number;
	title: string;
}

export interface Metadata {
	start_date: string
	end_date: string
	total_records: number
}
  

export async function fetchSpentTime(): Promise<SpentTime[] | null> {
	try {
		const response = await fetch("/api/spent_time");

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch tracks';
			console.log(error);
			return null;
		}

		const data = (await response.json());
		return JSON.parse(data);
	} catch (err) {
		console.log(err);
		return null;
	}
}


export async function fetchMetadata(): Promise<Metadata | null> {
	try {
		const response = await fetch("/api/dataset_metadata");

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch tracks';
			console.log(error);
			return null;
		}

		let data = (await response.json()) as Metadata;
		data.start_date = new Date(data.start_date).toLocaleDateString();
		data.end_date = new Date(data.end_date).toLocaleDateString();
		return data; 
	} catch (err) {
		console.log(err);
		return null;
	}
}

