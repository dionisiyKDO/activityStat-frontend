# ActivityStat Frontend

The frontend for **ActivityStat**, a web application that visualizes computer activity statistics, such as time spent on specific apps or games. This project uses API endpoints from [ActivityStat Backend](https://github.com/dionisiyKDO/activityStat-backend) for fetching parsed data, and displays it in interactive charts.

Built with:

- **Svelte 5**: For a reactive and efficient UI.
- **Tailwind CSS**: For styling and responsive design.
- **D3.js**: For creating interactive and dynamic data visualizations.

## Features

- Bar chart showing total time spent per application.
- Timeline chart and Calendar heatmap for daily usage

## Setup

1. Clone this repository:

    ```bash
    git clone https://github.com/dionisiyKDO/activityStat-frontend
    cd activitystat-frontend
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Run development server:

    ```bash
    npm run dev
    ```

4. Build for production:

    ```bash
    npm run build
    ```

## Frontend Routes

### `/`
Redirects to `/spent_time`.

### `/spent_time`
Bar chart (top 10 apps), extended data table, and dataset metadata.

### `/daily_app_usage`
Multi-select apps -> line chart (per app) and calendar heatmap (total daily usage for selected apps).

## Requirements

- Node.js 16+
- ActivityWatch data export
- Running instance of [ActivityStat Backend](https://github.com/dionisiyKDO/activityStat-backend).

## To Do

- [ ] Allow users to customize presets and save them to the backend.
- [ ] Test saving data that is fetched to the local storage, so that it can be used later without refetching.
- [ ] At least writelogic for not fetching data that is already fetched. Do not fetch data for apps that are already in the list.
- [ ] Add form to '/spent_time' for changing number of shown bars on chart

## Related

- [ActivityStat Backend](https://github.com/dionisiyKDO/activityStat-backend) — FastAPI service for parsing and querying ActivityWatcher data
