const csvInput = document.querySelector("#csv-input");
const statusBox = document.querySelector("#status");
const fileList = document.querySelector("#file-list");
const emptyState = document.querySelector("#empty-state");
const chart = document.querySelector("#trend-chart");

const fields = {
  readiness: document.querySelector("#readiness-value"),
  sleep: document.querySelector("#sleep-value"),
  sleepHours: document.querySelector("#sleep-hours-value"),
  hrv: document.querySelector("#hrv-value"),
  recommendationLevel: document.querySelector("#recommendation-level"),
  recommendationCopy: document.querySelector("#recommendation-copy"),
  recommendationDate: document.querySelector("#recommendation-date"),
  recordCount: document.querySelector("#record-count"),
};

csvInput.addEventListener("change", async (event) => {
  const files = Array.from(event.target.files || []);
  if (!files.length) return;

  try {
    const parsedFiles = await Promise.all(files.map(parseOuraFile));
    const records = parsedFiles
      .flatMap((file) => file.records)
      .sort((left, right) => left.day.localeCompare(right.day));

    renderFiles(parsedFiles);
    renderSummary(records);
    renderChart(records);
    showStatus(`Parsed ${records.length} usable rows from ${files.length} file(s).`, "success");
  } catch (error) {
    showStatus(error.message || "Could not parse the uploaded CSV files.", "error");
  }
});

async function parseOuraFile(file) {
  const text = await file.text();
  const rows = parseCsv(text);
  const records = rows
    .map((row) => normalizeRow(row, file.name))
    .filter((record) => record && record.day);

  return {
    name: file.name,
    records,
  };
}

function parseCsv(text) {
  const rows = [];
  let current = "";
  let row = [];
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (char === '"' && quoted && next === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(current);
      current = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && next === "\n") index += 1;
      row.push(current);
      rows.push(row);
      row = [];
      current = "";
    } else {
      current += char;
    }
  }

  if (current || row.length) {
    row.push(current);
    rows.push(row);
  }

  const cleanRows = rows.filter((candidate) => candidate.some((cell) => cell.trim()));
  const headers = (cleanRows.shift() || []).map(normalizeField);
  return cleanRows.map((dataRow) =>
    Object.fromEntries(headers.map((header, index) => [header, (dataRow[index] || "").trim()])),
  );
}

function normalizeRow(row, fileName) {
  const day = firstValue(row, ["day", "date", "timestamp"])?.slice(0, 10);
  if (!day) return null;

  const readinessScore = numberValue(row, [
    "readiness_score",
    "readiness",
    "daily_readiness_score",
  ]);
  const sleepScore = numberValue(row, ["sleep_score", "sleep", "daily_sleep_score"]);
  const score = numberValue(row, ["score"]);

  return {
    day,
    score,
    readinessScore,
    sleepScore,
    totalSleepHours: sleepHours(row),
    hrvBalance: numberValue(row, ["hrv_balance", "contributors_hrv_balance"]),
    sourceFile: fileName,
  };
}

function renderFiles(parsedFiles) {
  fileList.replaceChildren();
  emptyState.hidden = parsedFiles.length > 0;

  parsedFiles.forEach((file) => {
    const item = document.createElement("li");
    const name = document.createElement("span");
    const count = document.createElement("strong");
    name.textContent = file.name;
    count.textContent = `${file.records.length} usable rows`;
    item.append(name, count);
    fileList.append(item);
  });
}

function renderSummary(records) {
  fields.recordCount.textContent = `${records.length} records`;

  if (!records.length) {
    fields.readiness.textContent = "No data";
    fields.sleep.textContent = "No data";
    fields.sleepHours.textContent = "No data";
    fields.hrv.textContent = "No data";
    fields.recommendationLevel.textContent = "Upload CSV Data";
    fields.recommendationCopy.textContent = "Choose one or more Oura CSV exports to generate a local recovery summary.";
    fields.recommendationDate.textContent = "";
    return;
  }

  const latest = records[records.length - 1];
  fields.readiness.textContent = formatMetric(latest.readinessScore ?? latest.score);
  fields.sleep.textContent = formatMetric(latest.sleepScore);
  fields.sleepHours.textContent = formatMetric(latest.totalSleepHours);
  fields.hrv.textContent = formatMetric(latest.hrvBalance);

  const recommendation = getRecommendation(latest);
  fields.recommendationLevel.textContent = recommendation.level;
  fields.recommendationCopy.textContent = recommendation.copy;
  fields.recommendationDate.textContent = `Based on ${latest.day}`;
}

function renderChart(records) {
  const context = chart.getContext("2d");
  const width = chart.width;
  const height = chart.height;
  const padding = { top: 28, right: 28, bottom: 48, left: 52 };

  context.clearRect(0, 0, width, height);
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, width, height);

  const points = records
    .map((record) => ({
      day: record.day,
      readiness: record.readinessScore ?? record.score,
      sleep: record.sleepScore,
    }))
    .filter((point) => point.readiness !== undefined || point.sleep !== undefined);

  drawGrid(context, width, height, padding);

  if (points.length < 2) {
    context.fillStyle = "#68746e";
    context.font = "16px system-ui, sans-serif";
    context.textAlign = "center";
    context.fillText("Upload at least two dated rows to draw a trend.", width / 2, height / 2);
    return;
  }

  drawLine(context, points, "readiness", "#176f5d", width, height, padding);
  drawLine(context, points, "sleep", "#b9622f", width, height, padding);
  drawLabels(context, points, width, height, padding);
}

function drawGrid(context, width, height, padding) {
  context.strokeStyle = "#e6ebe7";
  context.lineWidth = 1;
  context.fillStyle = "#68746e";
  context.font = "12px system-ui, sans-serif";
  context.textAlign = "right";

  [0, 25, 50, 75, 100].forEach((tick) => {
    const y = scoreToY(tick, height, padding);
    context.beginPath();
    context.moveTo(padding.left, y);
    context.lineTo(width - padding.right, y);
    context.stroke();
    context.fillText(String(tick), padding.left - 10, y + 4);
  });
}

function drawLine(context, points, key, color, width, height, padding) {
  context.strokeStyle = color;
  context.lineWidth = 4;
  context.lineCap = "round";
  context.lineJoin = "round";
  context.beginPath();

  points.forEach((point, index) => {
    if (point[key] === undefined) return;
    const x = indexToX(index, points.length, width, padding);
    const y = scoreToY(point[key], height, padding);
    if (index === 0) context.moveTo(x, y);
    else context.lineTo(x, y);
  });

  context.stroke();
}

function drawLabels(context, points, width, height, padding) {
  context.fillStyle = "#68746e";
  context.font = "12px system-ui, sans-serif";
  context.textAlign = "center";

  points.forEach((point, index) => {
    const x = indexToX(index, points.length, width, padding);
    context.fillText(point.day.slice(5), x, height - 18);
  });
}

function getRecommendation(record) {
  const readinessScore = record.readinessScore ?? record.score;
  const totalSleepHours = record.totalSleepHours;

  if (readinessScore === undefined || totalSleepHours === undefined) {
    return {
      level: "Unknown",
      copy: "Upload readiness and sleep exports with score and sleep duration fields to generate a recommendation.",
    };
  }

  if (readinessScore >= 85 && totalSleepHours >= 7.5) {
    return {
      level: "Optimal",
      copy: "Good recovery signal for a harder workout if that already matches the plan.",
    };
  }

  if (readinessScore >= 70 && totalSleepHours >= 7) {
    return {
      level: "Moderate",
      copy: "Proceed, but keep intensity honest and avoid forcing pace if effort feels off.",
    };
  }

  return {
    level: "Fatigue",
    copy: "Bias toward easy movement, mobility, walking, or a relaxed Zone 2 session.",
  };
}

function sleepHours(row) {
  const directHours = numberValue(row, ["total_sleep_hours", "sleep_hours"]);
  if (directHours !== undefined) return directHours;

  const seconds = numberValue(row, [
    "total_sleep",
    "total_sleep_duration",
    "contributors_total_sleep",
  ]);
  if (seconds !== undefined) return Math.round((seconds / 3600) * 100) / 100;

  return undefined;
}

function normalizeField(value) {
  return value.trim().toLowerCase().replace(/\s+/g, "_").replace(/[.-]/g, "_");
}

function firstValue(row, keys) {
  for (const key of keys) {
    if (row[key]) return row[key];
  }
  return undefined;
}

function numberValue(row, keys) {
  const value = firstValue(row, keys);
  if (!value) return undefined;
  const parsed = Number(value.replace(/,/g, ""));
  return Number.isFinite(parsed) ? parsed : undefined;
}

function formatMetric(value) {
  return value === undefined ? "No data" : String(value);
}

function indexToX(index, total, width, padding) {
  return padding.left + (index / Math.max(total - 1, 1)) * (width - padding.left - padding.right);
}

function scoreToY(score, height, padding) {
  const bounded = Math.max(0, Math.min(score, 100));
  return height - padding.bottom - (bounded / 100) * (height - padding.top - padding.bottom);
}

function showStatus(message, tone) {
  statusBox.textContent = message;
  statusBox.className = `status ${tone}`;
  statusBox.hidden = false;
}
