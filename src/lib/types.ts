export interface margin {
	top: number;
	right: number;
	bottom: number;
	left: number;
}

// Daily app usage
export interface AppUsageData {
	timestamp: number;
	date: Date | null;
	app: string;
	duration: number;
}

export interface RawAppUsageData {
	date: number;
	duration: number;
}

export interface App {
	app: string[];
	title: string;
}

// Spent time
export interface SpentTime {
	app: string;
	duration: number;
	title: string;
}

export interface Metadata {
	start_date: string | Date;
	end_date: string | Date;
	total_records: number;
}
