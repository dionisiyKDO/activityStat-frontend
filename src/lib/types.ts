export interface margin {
	top: number;
	right: number;
	bottom: number;
	left: number;
}

// Daily app usage
export interface AppUsageData {
	date: Date | null;
	app: string;
	duration: number;
}

export interface RawAppUsageData {
	date: number;
	app: Text;
	duration: number;
}

export interface App {
	app: string[];
	title: string;
}

// Daily OS usage 
export interface OSUsageData {
	date: Date | null;
	platform: string;
	duration: number;
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
