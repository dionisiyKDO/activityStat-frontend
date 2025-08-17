import { type SpentTime, type Metadata } from '$lib/types';

export async function fetchSpentTime(): Promise<SpentTime[] | null> {
	try {
		const response = await fetch(`/api/spent_time`);

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch time';
			console.log(error);
			return null;
		}

		const data: SpentTime[] = await response.json();
		return data;
	} catch (err) {
		console.log(err);
		return null;
	}
}

export async function fetchMetadata(): Promise<Metadata | null> {
	try {
		const response = await fetch(`/api/dataset_metadata`);

		if (!response.ok) {
			const data = await response.json();
			const error = data.error || 'Failed to fetch metadata';
			console.log(error);
			return null;
		}

		let data: Metadata = await response.json();

		data.start_date = new Date(data.start_date).toLocaleDateString();
		data.end_date = new Date(data.end_date).toLocaleDateString();

		return data;
	} catch (err) {
		console.log(err);
		return null;
	}
}
