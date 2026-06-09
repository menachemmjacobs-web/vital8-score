const metrics = [
  {
    name: "Blood Pressure",
    group: "cardiovascular",
    score: 75,
    status: "Normal",
    value: "131 / 87 mmHg",
    anchor: "Ideal: below 120 / 80 mmHg",
    ring: "#0f3a53",
    spark: "M4 42 C50 42 82 38 120 28 S198 10 260 10",
    stats: [
      ["Avg systolic", "137", "mmHg"],
      ["Avg diastolic", "83", "mmHg"],
      ["Max systolic BP", "160", "mmHg"],
      ["Min systolic BP", "115", "mmHg"]
    ]
  },
  {
    name: "Blood Lipids",
    group: "cardiovascular",
    score: 85,
    status: "Normal",
    value: "Non-HDL 121 mg/dL",
    anchor: "Ideal: non-HDL below 130 mg/dL",
    ring: "#f47f2d",
    spark: "M4 30 C34 28 38 42 58 42 S84 18 104 18 S130 40 150 40 S172 16 196 16 S222 42 258 42",
    stats: [
      ["Latest non-HDL", "121", "mg/dL"],
      ["ApoB", "74", "mg/dL"],
      ["Reference", "<130", "mg/dL"],
      ["Score", "85", "/100"]
    ]
  },
  {
    name: "Physical Activity",
    group: "cardiovascular",
    score: 100,
    status: "Normal",
    value: "206 min/week",
    anchor: "Ideal: 150+ min moderate weekly",
    ring: "#f7c861",
    spark: "M4 44 C24 42 30 28 44 28 S58 50 76 42 S96 16 112 24 S132 34 148 32 S164 18 178 18 S196 54 258 44",
    stats: [
      ["Weekly minutes", "206", "min"],
      ["AHA target", "150", "min"],
      ["Days active", "5", "days"],
      ["Score", "100", "/100"]
    ]
  },
  {
    name: "Nicotine Exposure",
    group: "cardiovascular",
    score: 100,
    status: "Normal",
    value: "Never smoker",
    anchor: "Ideal: no inhaled nicotine exposure",
    ring: "#eee8bd",
    spark: "M4 32 L44 32 L84 32 L124 32 L164 32 L204 32 L258 32",
    stats: [
      ["Use status", "None", ""],
      ["Secondhand", "No", ""],
      ["AHA score", "100", "/100"],
      ["Focus", "Maintain", ""]
    ]
  },
  {
    name: "Blood Glucose",
    group: "metabolic",
    score: 60,
    status: "Focus",
    value: "HbA1c 5.9%",
    anchor: "Ideal: HbA1c below 5.7% or FBG below 100",
    ring: "#cc3832",
    spark: "M4 22 C30 30 42 18 62 22 S96 44 118 38 S148 12 172 24 S200 52 258 32",
    stats: [
      ["Latest HbA1c", "5.9", "%"],
      ["Fasting glucose", "108", "mg/dL"],
      ["Classic score", "60", "/100"],
      ["Target", "<5.7", "%"]
    ]
  },
  {
    name: "Body Mass Index",
    group: "metabolic",
    score: 70,
    status: "Normal",
    value: "28.9 kg/m2",
    anchor: "Ideal: BMI below 25 kg/m2",
    ring: "#f47f2d",
    spark: "M4 24 C42 24 54 42 92 38 S126 16 164 28 S212 54 258 14",
    stats: [
      ["Latest BMI", "28.9", "kg/m2"],
      ["Classic band", "25-29.9", ""],
      ["Score", "70", "/100"],
      ["Target", "<25", "kg/m2"]
    ]
  },
  {
    name: "Sleep Duration",
    group: "metabolic",
    score: 80,
    status: "Normal",
    value: "6.8 hours/night",
    anchor: "Ideal: 7 to under 9 hours nightly",
    ring: "#f7c861",
    spark: "M4 26 C18 44 34 46 46 18 S76 6 96 16 S120 52 144 36 S176 12 204 22 S232 28 258 20",
    stats: [
      ["Average sleep", "6.8", "hours"],
      ["AHA target", "7-9", "hours"],
      ["Trend", "+0.1", "hours"],
      ["Score", "80", "/100"]
    ]
  },
  {
    name: "Diet Quality",
    group: "metabolic",
    score: 25,
    status: "Focus",
    value: "MEPA needs assessment",
    anchor: "Ideal: high DASH or Mediterranean adherence",
    ring: "#cc3832",
    spark: "M4 40 C20 36 34 16 54 28 S86 52 106 36 S134 12 158 32 S196 50 258 24",
    stats: [
      ["Current score", "25", "/100"],
      ["Assessment", "Open", ""],
      ["Food pattern", "MEPA", ""],
      ["Target", "80+", "/100"]
    ]
  }
];

const metricRows = document.querySelector("#metricRows");
const splitButtons = document.querySelectorAll(".score-pill");
const overallScoreText = document.querySelector("#overallScoreText");
const overallScoreLabel = document.querySelector("#overallScoreLabel");
const surveyForm = document.querySelector("#surveyForm");
const saveSurvey = document.querySelector("#saveSurvey");
const labUpload = document.querySelector("#labUpload");
const labFileName = document.querySelector("#labFileName");
const labNotes = document.querySelector("#labNotes");
const labInsights = document.querySelector("#labInsights");
const coachForm = document.querySelector("#coachForm");
const coachQuestion = document.querySelector("#coachQuestion");
const coachThread = document.querySelector("#coachThread");
const modal = document.querySelector("#modalBackdrop");
const closeModal = document.querySelector("#closeModal");
const modalTitle = document.querySelector("#modalTitle");
const modalSubtitle = document.querySelector("#modalSubtitle");
const modalStats = document.querySelector("#modalStats");
let activeGroup = "cardiovascular";
let latestLabs = [];

const scoreColor = {
  navy: "#0f3a53",
  red: "#cc3832",
  orange: "#f47f2d",
  yellow: "#f7c861",
  cream: "#eee8bd"
};

function renderGauge() {
  const gaugeBars = document.querySelector("#gaugeBars");
  for (let index = 0; index < 38; index += 1) {
    const segment = document.createElement("span");
    const angle = -92 + index * 4.95;
    segment.className = "gauge-segment";
    segment.style.transform = `rotate(${angle}deg)`;
    if (index < 25) {
      segment.classList.add("filled");
      if (index < 11) segment.classList.add("low");
      else if (index < 21) segment.classList.add("mid");
      else segment.classList.add("high");
    }
    gaugeBars.appendChild(segment);
  }
}

function renderRows() {
  metricRows.innerHTML = "";
  metrics
    .filter((metric) => metric.group === activeGroup)
    .forEach((metric) => {
      const row = document.createElement("button");
      row.className = "metric-row";
      row.type = "button";
      row.innerHTML = `
        <div class="metric-name">
          <strong>${metric.name}</strong>
          <span>${metric.anchor}</span>
        </div>
        <div class="score-cell">
          <div class="ring" style="--score: ${metric.score}; --ring: ${metric.ring}">
            <span>${metric.score}</span>
          </div>
          <div class="score-detail">
            <b class="status ${metric.status === "Focus" ? "focus" : ""}">${metric.status}</b>
            <span>${metric.value}</span>
          </div>
        </div>
        <svg class="sparkline" viewBox="0 0 262 60" aria-hidden="true">
          <path d="${metric.spark}" style="stroke: ${metric.ring}"></path>
        </svg>
        <span class="chev">›</span>
      `;
      row.addEventListener("click", () => openMetric(metric));
      metricRows.appendChild(row);
    });
}

function scoreActivity(minutes) {
  if (minutes >= 150) return 100;
  if (minutes >= 120) return 90;
  if (minutes >= 90) return 80;
  if (minutes >= 60) return 60;
  if (minutes >= 30) return 40;
  if (minutes > 0) return 20;
  return 0;
}

function scoreSleep(hours) {
  if (hours >= 7 && hours < 9) return 100;
  if (hours >= 9 && hours < 10) return 90;
  if (hours >= 6 && hours < 7) return 70;
  if ((hours >= 5 && hours < 6) || hours >= 10) return 40;
  if (hours >= 4 && hours < 5) return 20;
  return 0;
}

function scoreBloodPressure(systolic, diastolic) {
  if (systolic < 120 && diastolic < 80) return 100;
  if (systolic < 130 && diastolic < 80) return 75;
  if (systolic < 140 || diastolic < 90) return 50;
  if (systolic < 160 || diastolic < 100) return 25;
  return 0;
}

function scoreBmi(bmi) {
  if (bmi < 25) return 100;
  if (bmi < 30) return 70;
  if (bmi < 35) return 30;
  if (bmi < 40) return 15;
  return 0;
}

function scoreA1c(a1c) {
  if (a1c < 5.7) return 100;
  if (a1c < 6.5) return 60;
  if (a1c < 7) return 40;
  if (a1c < 8) return 30;
  if (a1c < 9) return 20;
  if (a1c < 10) return 10;
  return 0;
}

function scoreNonHdl(nonHdl) {
  if (nonHdl < 130) return 100;
  if (nonHdl < 160) return 60;
  if (nonHdl < 190) return 40;
  if (nonHdl < 220) return 20;
  return 0;
}

function scoreLabel(score) {
  if (score >= 80) return "High";
  if (score >= 50) return "Good";
  return "Focus";
}

function metricStatus(score) {
  return score >= 50 ? "Normal" : "Focus";
}

function updateMetric(name, updates) {
  const metric = metrics.find((item) => item.name === name);
  Object.assign(metric, updates);
}

function getSurveyValues() {
  const data = new FormData(surveyForm);
  return {
    activity: Number(data.get("activity")),
    sleep: Number(data.get("sleep")),
    diet: Number(data.get("diet")),
    nicotine: Number(data.get("nicotine")),
    systolic: Number(data.get("systolic")),
    diastolic: Number(data.get("diastolic")),
    bmi: Number(data.get("bmi")),
    a1c: Number(data.get("a1c")),
    nonHdl: Number(data.get("nonHdl"))
  };
}

function recalculateScores() {
  const values = getSurveyValues();
  const bpScore = scoreBloodPressure(values.systolic, values.diastolic);
  const lipidScore = scoreNonHdl(values.nonHdl);
  const activityScore = scoreActivity(values.activity);
  const nicotineScore = values.nicotine;
  const glucoseScore = scoreA1c(values.a1c);
  const bmiScore = scoreBmi(values.bmi);
  const sleepScore = scoreSleep(values.sleep);
  const dietScore = values.diet;

  updateMetric("Blood Pressure", {
    score: bpScore,
    status: metricStatus(bpScore),
    value: `${values.systolic} / ${values.diastolic} mmHg`,
    ring: bpScore < 50 ? scoreColor.red : scoreColor.navy
  });
  updateMetric("Blood Lipids", {
    score: lipidScore,
    status: metricStatus(lipidScore),
    value: `Non-HDL ${values.nonHdl} mg/dL`,
    ring: lipidScore < 50 ? scoreColor.red : scoreColor.orange
  });
  updateMetric("Physical Activity", {
    score: activityScore,
    status: metricStatus(activityScore),
    value: `${values.activity} min/week`,
    ring: activityScore >= 80 ? scoreColor.yellow : scoreColor.orange
  });
  updateMetric("Nicotine Exposure", {
    score: nicotineScore,
    status: metricStatus(nicotineScore),
    value: nicotineScore === 100 ? "No exposure" : "Exposure reported",
    ring: nicotineScore < 50 ? scoreColor.red : scoreColor.cream
  });
  updateMetric("Blood Glucose", {
    score: glucoseScore,
    status: metricStatus(glucoseScore),
    value: `HbA1c ${values.a1c}%`,
    ring: glucoseScore < 50 ? scoreColor.red : scoreColor.orange
  });
  updateMetric("Body Mass Index", {
    score: bmiScore,
    status: metricStatus(bmiScore),
    value: `${values.bmi} kg/m2`,
    ring: bmiScore < 50 ? scoreColor.red : scoreColor.orange
  });
  updateMetric("Sleep Duration", {
    score: sleepScore,
    status: metricStatus(sleepScore),
    value: `${values.sleep} hours/night`,
    ring: sleepScore >= 80 ? scoreColor.yellow : scoreColor.orange
  });
  updateMetric("Diet Quality", {
    score: dietScore,
    status: metricStatus(dietScore),
    value: dietScore < 50 ? "MEPA needs assessment" : "Diet pattern logged",
    ring: dietScore < 50 ? scoreColor.red : scoreColor.yellow
  });

  const overall = Math.round(metrics.reduce((sum, metric) => sum + metric.score, 0) / metrics.length);
  const cardiovascular = Math.round(groupAverage("cardiovascular"));
  const metabolic = Math.round(groupAverage("metabolic"));
  overallScoreText.textContent = overall;
  overallScoreLabel.textContent = scoreLabel(overall);
  splitButtons[0].querySelector("strong").textContent = cardiovascular;
  splitButtons[1].querySelector("strong").textContent = metabolic;
  renderRows();
  return { overall, cardiovascular, metabolic, values };
}

function groupAverage(group) {
  const groupMetrics = metrics.filter((metric) => metric.group === group);
  return groupMetrics.reduce((sum, metric) => sum + metric.score, 0) / groupMetrics.length;
}

function saveWeeklySnapshot() {
  const snapshot = {
    date: new Date().toISOString(),
    scores: recalculateScores(),
    metrics: metrics.map(({ name, score, value }) => ({ name, score, value }))
  };
  const history = JSON.parse(localStorage.getItem("vital8History") || "[]");
  history.unshift(snapshot);
  localStorage.setItem("vital8History", JSON.stringify(history.slice(0, 26)));
  addCoachMessage("Coach", "Weekly check-in saved locally. Your current lowest-return opportunities are now reflected in the score table and coach context.");
}

function parseLabs(text) {
  const patterns = [
    { key: "ApoB", label: "ApoB", regex: /apo\s?b[^0-9]*(\d+(\.\d+)?)/i, high: 90, unit: "mg/dL" },
    { key: "hsCRP", label: "hs-CRP", regex: /hs[-\s]?crp[^0-9]*(\d+(\.\d+)?)/i, high: 2, unit: "mg/L" },
    { key: "Lp(a)", label: "Lp(a)", regex: /lp\s?\(?a\)?[^0-9]*(\d+(\.\d+)?)/i, high: 30, unit: "mg/dL" },
    { key: "LDL-C", label: "LDL-C", regex: /ldl[-\s]?c?[^0-9]*(\d+(\.\d+)?)/i, high: 100, unit: "mg/dL" },
    { key: "TG", label: "Triglycerides", regex: /(?:triglycerides|tg)[^0-9]*(\d+(\.\d+)?)/i, high: 150, unit: "mg/dL" }
  ];

  latestLabs = patterns
    .map((marker) => {
      const match = text.match(marker.regex);
      if (!match) return null;
      const value = Number(match[1]);
      return { ...marker, value, elevated: value > marker.high };
    })
    .filter(Boolean);

  renderLabInsights();
}

function renderLabInsights() {
  if (!latestLabs.length) {
    labInsights.innerHTML = "<strong>Waiting for labs</strong><span>Add values to surface prevention markers for the AI coach.</span>";
    return;
  }
  const elevated = latestLabs.filter((marker) => marker.elevated);
  const summary = elevated.length
    ? `${elevated.map((marker) => marker.label).join(", ")} flagged for clinician review.`
    : "No pasted marker crossed the prototype threshold.";
  labInsights.innerHTML = `
    <strong>${summary}</strong>
    <span>${latestLabs.map((marker) => `${marker.label}: ${marker.value} ${marker.unit}`).join(" · ")}</span>
  `;
}

function lowestMetrics() {
  return [...metrics].sort((a, b) => a.score - b.score).slice(0, 3);
}

function addCoachMessage(author, message) {
  const item = document.createElement("div");
  item.className = author === "You" ? "user-message" : "coach-message";
  item.innerHTML = `<strong>${author}</strong><p>${message}</p>`;
  coachThread.appendChild(item);
  coachThread.scrollTop = coachThread.scrollHeight;
}

function coachReply(question) {
  const lower = question.toLowerCase();
  const low = lowestMetrics();
  const labFlags = latestLabs.filter((marker) => marker.elevated);

  if (lower.includes("sleep") && (lower.includes("apob") || lower.includes("ldl") || lower.includes("statin"))) {
    return "I would split this into two lanes. Sleep is a high-ROI behavior target because it can affect blood pressure, glucose, appetite, and training consistency. ApoB/LDL-C is a risk-marker lane: if elevated, the app should explain particle burden, show lifestyle levers, and prompt a clinician discussion about whether medication such as a statin fits the person's absolute risk and goals.";
  }
  if (lower.includes("sleep")) {
    return "Sleep is a high-ROI lever because it affects the LE8 score directly and can also influence appetite, blood pressure, glucose, and training consistency. A good first experiment is a fixed wake time, morning light, caffeine cutoff, and a 30-minute wind-down window for two weeks.";
  }
  if (lower.includes("statin") || lower.includes("apob") || lower.includes("ldl")) {
    return "For prevention, ApoB/non-HDL/LDL-C help estimate atherogenic particle burden. If ApoB or LDL-C is elevated, the app should explain lifestyle options and prompt a clinician discussion about medication fit, risks, benefits, and personal risk context.";
  }
  if (lower.includes("glp") || lower.includes("weight")) {
    return "GLP-1 discussions belong in a clinician workflow. From a score perspective, the app can frame weight, glucose, blood pressure, sleep, and activity together so the person sees whether medication, nutrition, resistance training, or sleep work is likely to produce the best return.";
  }
  if (lower.includes("crp") || lower.includes("inflammation")) {
    return "hs-CRP can be a useful inflammation signal, but it is nonspecific. The app should pair it with context: infection, training load, sleep, adiposity, oral health, autoimmune issues, and cardiovascular risk markers like ApoB and Lp(a).";
  }
  if (labFlags.length) {
    return `Based on the pasted labs, I would prioritize explaining ${labFlags.map((marker) => marker.label).join(", ")} and connecting those markers to the lowest LE8 areas: ${low.map((metric) => metric.name).join(", ")}. This is educational support, not a diagnosis.`;
  }
  return `Your current lowest scoring areas are ${low.map((metric) => `${metric.name} (${metric.score})`).join(", ")}. The best first coaching move is to pick one behavior with a clear weekly target, then re-score next week.`;
}

function openMetric(metric) {
  modalTitle.textContent = metric.name;
  modalSubtitle.textContent = "Last 30 days";
  modalStats.innerHTML = metric.stats
    .map(([label, value, unit]) => `
      <div class="stat-card">
        <span>${label}</span>
        <strong>${value}</strong>
        <small>${unit}</small>
      </div>
    `)
    .join("");
  modal.hidden = false;
}

splitButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeGroup = button.dataset.filter;
    splitButtons.forEach((item) => item.classList.toggle("active", item === button));
    renderRows();
  });
});

surveyForm.addEventListener("input", () => {
  recalculateScores();
});

saveSurvey.addEventListener("click", () => {
  saveWeeklySnapshot();
});

labUpload.addEventListener("change", () => {
  const file = labUpload.files[0];
  labFileName.textContent = file ? file.name : "PDF, image, CSV, or text";
});

labNotes.addEventListener("input", () => {
  parseLabs(labNotes.value);
});

coachForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = coachQuestion.value.trim();
  if (!question) return;
  addCoachMessage("You", question);
  addCoachMessage("Coach", coachReply(question));
  coachQuestion.value = "";
});

closeModal.addEventListener("click", () => {
  modal.hidden = true;
});

modal.addEventListener("click", (event) => {
  if (event.target === modal) modal.hidden = true;
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") modal.hidden = true;
});

renderGauge();
recalculateScores();
renderRows();
