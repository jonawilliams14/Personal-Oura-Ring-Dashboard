# Native JavaScript Frontend

This frontend is intentionally dependency-free:

- `index.html`
- `styles.css`
- `app.js`

Open `index.html` directly in a browser, or serve the folder with any static file server.

## Data Flow

1. The user chooses one or more Oura CSV exports.
2. The browser reads files with the File API.
3. CSV rows are parsed locally in `app.js`.
4. The dashboard renders metrics, a recommendation, uploaded-file counts, and a trend chart.

No CSV content is uploaded to a server.
