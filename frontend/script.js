"use strict";

const state = {
    locale: "en-IN",
    currency: "₹",
    analytics: null,
    validation: null,
    charts: [],
    currentFileName: null,
    isUploading: false
};

const $id = (id) => document.getElementById(id);

function setText(id, value) {
    const element = $id(id);
    if (element) element.textContent = value ?? "—";
}

function showSection(...ids) {
    ids.forEach((id) => {
        const element = $id(id);
        if (element) element.classList.remove("is-hidden");
    });
    $id("emptyState")?.classList.add("is-hidden");
}

function fmtNumber(value) {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    if (Number.isNaN(number)) return String(value);
    try {
        return new Intl.NumberFormat(state.locale).format(number);
    } catch {
        return number.toLocaleString("en-IN");
    }
}

function fmtCurrency(value) {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    if (Number.isNaN(number)) return String(value);
    return state.currency + fmtNumber(Math.round(number));
}

function fmtDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    return `${day}/${month}/${yearOf(date)}`;
}

function yearOf(date) {
    return date.getFullYear();
}

function esc(value) {
    const div = document.createElement("div");
    div.textContent = value == null ? "" : String(value);
    return div.innerHTML;
}

function showToast(message, type = "success") {
    const host = $id("toastHost");
    if (!host) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${type === "success" ? "✓" : "⚠"}</span>
        <span>${esc(message)}</span>
    `;

    host.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity .4s";
        setTimeout(() => toast.remove(), 400);
    }, 4200);
}

function setStatus(message, type = "") {
    const status = $id("status");
    if (!status) return;
    status.textContent = message || "";
    status.className = `status ${type}`.trim();
}

function resetPipeline() {
    const track = $id("pipelineTrack");
    if (track) track.hidden = false;

    document.querySelectorAll(".pipeline-step").forEach((step) => {
        step.classList.remove("active", "done");
    });
}

function setStep(name, phase) {
    const step = document.querySelector(`.pipeline-step[data-step="${name}"]`);
    if (!step) return;
    step.classList.toggle("active", phase === "active");
    step.classList.toggle("done", phase === "done");
}

async function apiGet(url) {
    const response = await fetch(url);
    let payload = null;

    try {
        payload = await response.json();
    } catch {

    }

    if (!response.ok) {
        const detail = payload && payload.detail
            ? payload.detail
            : `Request failed (${response.status})`;
        const error = new Error(detail);
        error.status = response.status;
        throw error;
    }

    return payload;
}

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const icon = $id("themeIcon");
    if (icon) icon.textContent = theme === "dark" ? "☀" : "☾";

    try {
        localStorage.setItem("sbi-theme", theme);
    } catch {

    }

    if (state.analytics) renderAnalyticsCharts(state.analytics);
}

function initTheme() {
    let saved = null;
    try {
        saved = localStorage.getItem("sbi-theme");
    } catch {

    }

    const prefersDark =
        window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;

    applyTheme(saved || (prefersDark ? "dark" : "light"));

    $id("themeToggle")?.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        applyTheme(current === "dark" ? "light" : "dark");
    });
}

function initSidebar() {
    const sidebar = $id("sidebar");
    const backdrop = $id("sidebarBackdrop");
    const toggle = $id("sidebarToggle");
    if (!sidebar || !toggle) return;

    const closeMobileNav = () => {
        sidebar.classList.remove("open");
        backdrop?.classList.remove("show");
    };

    toggle.addEventListener("click", () => {
        if (window.matchMedia("(max-width: 1024px)").matches) {
            sidebar.classList.toggle("open");
            backdrop?.classList.toggle("show", sidebar.classList.contains("open"));
        } else {
            document.body.classList.toggle("nav-collapsed");
        }
    });

    backdrop?.addEventListener("click", closeMobileNav);

    document.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", () => {
            document
                .querySelectorAll(".nav-link")
                .forEach((item) => item.classList.remove("is-active"));
            link.classList.add("is-active");
            closeMobileNav();
        });
    });

    const sections = Array.from(document.querySelectorAll("section[id]"));

    if ("IntersectionObserver" in window && sections.length) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    const target = entry.target.id;
                    document.querySelectorAll(".nav-link").forEach((link) => {
                        link.classList.toggle(
                            "is-active",
                            link.dataset.section === target
                        );
                    });
                });
            },
            { rootMargin: "-30% 0px -60% 0px" }
        );

        sections.forEach((section) => observer.observe(section));
    }
}

async function loadHealth() {
    const dot = $id("healthDot");
    const text = $id("healthText");

    try {
        const health = await apiGet("/api/system/health");

        if (health.currency) state.currency = health.currency;
        if (health.locale) state.locale = health.locale;

        const dbConnected = health.database && health.database.connected;

        dot?.classList.add(dbConnected ? "ok" : "bad");
        if (text) {
            text.textContent = dbConnected
                ? "Operational"
                : "DB issue";
        }

        if (
            health.latest_dataset &&
            health.latest_dataset.file_name &&
            !state.isUploading
        ) {
            await loadWorkspace(false);
            setStatus(
                `Showing saved analysis for "${health.latest_dataset.file_name}". Upload a new file to re-run.`,
                "ok"
            );
        }
    } catch {
        dot?.classList.add("bad");
        if (text) text.textContent = "Offline";
    }
}

function initUpload() {
    const dropzone = $id("dropzone");
    const fileInput = $id("fileInput");
    const analyzeButton = $id("analyzeButton");
    const dropTitle = $id("dropTitle");
    if (!dropzone || !fileInput || !analyzeButton) return;

    dropzone.addEventListener("click", (event) => {
        if (event.target.closest("button")) return;
        fileInput.click();
    });

    dropzone.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            fileInput.click();
        }
    });

    ["dragenter", "dragover"].forEach((eventName) =>
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.add("dragover");
        })
    );

    ["dragleave", "drop"].forEach((eventName) =>
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.remove("dragover");
        })
    );

    dropzone.addEventListener("drop", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            updateFileSelection();
        }
    });

    fileInput.addEventListener("change", updateFileSelection);

    function updateFileSelection() {
        if (fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            if (dropTitle) dropTitle.textContent = file.name;
            analyzeButton.disabled = false;
            setStatus(
                `Selected ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB). Ready to analyze.`,
                "ok"
            );
        } else {
            if (dropTitle) dropTitle.textContent = "Drag & drop your dataset here";
            analyzeButton.disabled = true;
        }
    }

    analyzeButton.addEventListener("click", runAnalysis);
}

async function runAnalysis() {
    const fileInput = $id("fileInput");
    const analyzeButton = $id("analyzeButton");

    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        setStatus("Please select a CSV or Excel file first.", "error");
        return;
    }

    state.isUploading = true;
    analyzeButton.disabled = true;
    resetPipeline();
    setStatus("Uploading dataset…");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const failures = [];

    const runPhase = async (stepName, label, loader) => {
        setStep(stepName, "active");
        setStatus(`${label}…`);
        try {
            await loader();
            setStep(stepName, "done");
        } catch (error) {
            setStep(stepName, "active");
            failures.push(`${label}: ${error.message}`);
            console.error(`${label} failed:`, error);
        }
    };

    try {

        setStep("upload", "active");

        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Dataset upload failed.");
        }

        setStep("upload", "done");
        state.currentFileName = data.file_name;

        await runPhase("kpi", "Loading KPIs, insights & data quality", async () => {
            await Promise.all([
                loadDashboardData(),
                loadInsights(),
                loadRecommendations(),
                loadAnomalies(),
                loadQuality()
            ]);
        });

        await runPhase("charts", "Rendering interactive analytics", () => loadAnalytics());

        await runPhase("forecast", "Training & validating the ML forecast", async () => {
            await Promise.all([loadForecast(), loadModelPerformance()]);
        });

        await runPhase("decisions", "Generating AI decision support", () => loadMLDecisions());

        await runPhase("inventory", "Computing inventory intelligence", () => loadInventory());

        await loadHistory().catch(() => {});

        if (failures.length === 0) {
            setStatus("Dataset analyzed successfully — full workspace activated.", "ok");
            showToast("Analysis complete");
        } else {
            setStatus(
                `Analysis finished with ${failures.length} warning(s): ${failures[0]}`,
                "error"
            );
            showToast(`Completed with warnings: ${failures[0]}`, "error");
        }
    } catch (error) {
        console.error("Analysis error:", error);
        setStatus(`Analysis failed: ${error.message}`, "error");
        showToast(`Analysis failed: ${error.message}`, "error");
    } finally {
        analyzeButton.disabled = false;
        state.isUploading = false;
    }
}

async function loadDashboardData() {
    const data = await apiGet("/api/dashboard");

    setText("overviewDataset", data.file_name || "—");
    setText("overviewRecords", fmtNumber(data.row_count || 0));
    setText("overviewProducts", fmtNumber(data.total_products || 0));
    setText("overviewForecastStatus", "Available");

    setText("totalRevenue", fmtCurrency(data.total_revenue));
    setText("totalQuantity", fmtNumber(data.total_quantity || 0));
    setText("totalProducts", fmtNumber(data.total_products || 0));
    setText("totalCustomers", fmtNumber(data.total_customers || 0));
    setText("totalLocations", fmtNumber(data.total_locations || 0));
    setText("kpiAvgPrice", fmtCurrency(data.average_price));

    if (data.average_order_value !== undefined) {
        setText("kpiAov", `AOV ${fmtCurrency(data.average_order_value)}`);
    }

    if (data.period_start && data.period_end) {
        setText("kpiPeriod", `${data.period_start} → ${data.period_end}`);
    }

    if (data.top_product) {
        setText("kpiTopProduct", `Top: ${data.top_product}`);
        setText("topProduct", data.top_product);
    }

    if (data.top_location) {
        setText("kpiTopLocation", `Top: ${data.top_location}`);
    }

    const summary = $id("overviewSummary");
    if (summary) {
        summary.textContent =
            `${data.file_name} — ${fmtNumber(data.row_count)} records · ` +
            `${fmtCurrency(data.total_revenue)} revenue · ` +
            `${fmtNumber(data.total_products)} products across ` +
            `${fmtNumber(data.total_locations || 0)} locations.`;
    }

    const topSub = $id("topbarSub");
    if (topSub) {
        topSub.textContent = `Analyzing: ${data.file_name} · ${fmtNumber(data.row_count)} records`;
    }

    showSection("section-overview", "section-kpi");
}

function cssVar(name) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(name)
        .trim();
}

function destroyCharts() {
    state.charts.forEach((chart) => chart.destroy());
    state.charts = [];
}

function chartTheme() {
    Chart.defaults.font.family = cssVar("--font") || "Inter, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = cssVar("--muted") || "#5c6b84";
    Chart.defaults.borderColor = cssVar("--line") || "#e3e8f2";
}

function emptyChart(canvasId, message) {
    const canvas = $id(canvasId);
    if (!canvas) return;
    const box = canvas.parentElement;
    if (!box) return;

    box.innerHTML = `<div class="chart-empty">${esc(message)}</div>`;
}

function chartEmptyStyle() {
    const style = document.createElement("style");
    if (!document.getElementById("chartEmptyStyle")) {
        style.id = "chartEmptyStyle";
        style.textContent =
            ".chart-empty{height:100%;display:grid;place-items:center;color:var(--muted);font-size:12.5px;text-align:center;padding:12px}";
        document.head.appendChild(style);
    }
}

function renderAnalyticsCharts(analytics) {
    destroyCharts();
    chartTheme();
    chartEmptyStyle();

    const gridColor = cssVar("--line");
    const textColor = cssVar("--text");
    const primary = cssVar("--primary");
    const accent = cssVar("--accent");

    const trend = analytics.revenue_trend || [];

    if (trend.length) {
        const canvas = $id("chartTrend");
        if (canvas) {
            state.charts.push(
                new Chart(canvas, {
                    data: {
                        labels: trend.map((point) => point.date),
                        datasets: [
                            {
                                type: "line",
                                label: "Revenue",
                                data: trend.map((point) => point.revenue),
                                borderColor: primary,
                                backgroundColor: `${primary}22`,
                                fill: true,
                                tension: 0.35,
                                pointRadius: trend.length > 40 ? 0 : 3,
                                borderWidth: 2,
                                yAxisID: "y"
                            },
                            ...(trend.some((point) => point.quantity)
                                ? [
                                      {
                                          type: "bar",
                                          label: "Quantity",
                                          data: trend.map((point) => point.quantity),
                                          backgroundColor: `${accent}55`,
                                          borderRadius: 4,
                                          yAxisID: "y1"
                                      }
                                  ]
                                : [])
                        ]
                    },
                    options: {
                        maintainAspectRatio: false,
                        interaction: { mode: "index", intersect: false },
                        plugins: {
                            legend: { position: "top", align: "end" },
                            tooltip: {
                                callbacks: {
                                    label: (context) =>
                                        `${context.dataset.label}: ${fmtNumber(context.parsed.y)}`
                                }
                            }
                        },
                        scales: {
                            y: {
                                position: "left",
                                grid: { color: gridColor },
                                ticks: { callback: (value) => fmtNumber(value) }
                            },
                            y1: {
                                position: "right",
                                grid: { drawOnChartArea: false },
                                ticks: { callback: (value) => fmtNumber(value) }
                            },
                            x: { grid: { display: false }, ticks: { maxTicksLimit: 12 } }
                        }
                    }
                })
            );
        }
    } else {
        emptyChart("chartTrend", "No dated records were found in this dataset, so a time trend cannot be drawn.");
    }

    const products = analytics.product_performance || [];

    if (products.length) {
        const canvas = $id("chartProducts");
        if (canvas) {
            state.charts.push(
                new Chart(canvas, {
                    type: "bar",
                    data: {
                        labels: products.map((item) => item.label),
                        datasets: [
                            {
                                label: "Revenue",
                                data: products.map((item) => item.value),
                                backgroundColor: products.map(
                                    (_, index) =>
                                        [primary, accent, "#10b981", "#f59e0b", "#ef4444"][index % 5] + "cc"
                                ),
                                borderRadius: 7
                            }
                        ]
                    },
                    options: {
                        indexAxis: "y",
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: (context) => fmtCurrency(context.parsed.x)
                                }
                            }
                        },
                        scales: {
                            x: { grid: { color: gridColor }, ticks: { callback: (v) => fmtNumber(v) } },
                            y: { grid: { display: false } }
                        }
                    }
                })
            );
        }
    } else {
        emptyChart("chartProducts", "No product column was detected in this dataset.");
    }

    const regions = analytics.regional_performance || [];

    if (regions.length) {
        const canvas = $id("chartRegions");
        if (canvas) {
            state.charts.push(
                new Chart(canvas, {
                    type: "doughnut",
                    data: {
                        labels: regions.map((item) => item.label),
                        datasets: [
                            {
                                data: regions.map((item) => item.value),
                                backgroundColor: [
                                    primary, accent, "#10b981", "#f59e0b",
                                    "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6"
                                ].map((color) => color + "dd"),
                                borderWidth: 2,
                                borderColor: cssVar("--surface"),
                                hoverOffset: 8
                            }
                        ]
                    },
                    options: {
                        maintainAspectRatio: false,
                        cutout: "58%",
                        plugins: {
                            legend: { position: "right" },
                            tooltip: {
                                callbacks: {
                                    label: (context) =>
                                        ` ${context.label}: ${fmtCurrency(context.parsed)}`
                                }
                            }
                        }
                    }
                })
            );
        }
    } else {
        emptyChart("chartRegions", "No location column was detected in this dataset.");
    }

    const categories = analytics.category_mix || [];

    if (categories.length) {
        const canvas = $id("chartCategory");
        if (canvas) {
            state.charts.push(
                new Chart(canvas, {
                    type: "polarArea",
                    data: {
                        labels: categories.map((item) => item.label),
                        datasets: [
                            {
                                data: categories.map((item) => item.value),
                                backgroundColor: [
                                    primary, accent, "#10b981", "#f59e0b",
                                    "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6"
                                ].map((color) => color + "99"),
                                borderWidth: 1,
                                borderColor: cssVar("--surface")
                            }
                        ]
                    },
                    options: {
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: "right" },
                            tooltip: {
                                callbacks: {
                                    label: (context) =>
                                        ` ${context.label}: ${fmtCurrency(context.parsed.r ?? context.parsed)}`
                                }
                            }
                        },
                        scales: {
                            r: { grid: { color: gridColor }, ticks: { display: false } }
                        }
                    }
                })
            );
        }
    } else {
        emptyChart("chartCategory", "No category column was detected in this dataset.");
    }

    const prices = analytics.price_distribution || [];

    if (prices.length) {
        const canvas = $id("chartPrice");
        if (canvas) {
            state.charts.push(
                new Chart(canvas, {
                    type: "bar",
                    data: {
                        labels: prices.map((item) => item.label),
                        datasets: [
                            {
                                label: "Records",
                                data: prices.map((item) => item.value),
                                backgroundColor: `${primary}bb`,
                                borderRadius: 5
                            }
                        ]
                    },
                    options: {
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
                            y: { grid: { color: gridColor } }
                        }
                    }
                })
            );
        }
    } else {
        emptyChart("chartPrice", "No price column was detected in this dataset.");
    }

    renderCorrelation(analytics.correlation);
}

function renderCorrelation(correlation) {
    const wrap = $id("correlationHeatmap");
    if (!wrap) return;

    const labels = (correlation && correlation.labels) || [];
    const values = (correlation && correlation.values) || [];

    if (!labels.length || !values.length) {
        wrap.innerHTML =
            '<div class="chart-empty">Fewer than two numeric columns — a correlation matrix is not applicable.</div>';
        return;
    }

    const header = labels
        .map((label) => `<th title="${esc(label)}">${esc(label)}</th>`)
        .join("");

    const body = values
        .map((row, rowIndex) => {
            const cells = row
                .map((value, columnIndex) => {
                    const safe = value === null ? 0 : value;
                    const intensity = Math.min(Math.abs(safe), 1);
                    const color =
                        safe >= 0
                            ? `rgba(79, 70, 229, ${(intensity * 0.75).toFixed(2)})`
                            : `rgba(224, 45, 60, ${(intensity * 0.75).toFixed(2)})`;
                    const textColor = intensity > 0.55 ? "#ffffff" : "inherit";
                    return `<td style="background:${color};color:${textColor}">${
                        value === null ? "—" : safe.toFixed(2)
                    }</td>`;
                })
                .join("");

            return `<tr><th>${esc(labels[rowIndex])}</th>${cells}</tr>`;
        })
        .join("");

    wrap.innerHTML = `<table class="corr-table"><thead><tr><th></th>${header}</tr></thead><tbody>${body}</tbody></table>`;
}

async function loadAnalytics() {
    const analytics = await apiGet("/api/dashboard/analytics");
    state.analytics = analytics;
    renderAnalyticsCharts(analytics);
    showSection("section-analytics");
}

function renderNoteCards(container, items, kind) {
    container.innerHTML = "";

    if (!items.length) {
        container.innerHTML = `<div class="card-note"><p>No ${kind} were generated for this dataset.</p></div>`;
        return;
    }

    items.forEach((item) => {
        const card = document.createElement("div");
        card.className = "card-note";

        if (typeof item === "string") {
            card.innerHTML = `<p>${esc(item)}</p>`;
        } else {
            const priority = (item.priority || item.severity || "").toString();
            const level = priority.toLowerCase();
            card.classList.add(`note-${level || "low"}`);

            const meta = [];
            if (item.area || item.product) {
                meta.push(`<strong>${esc(item.area || item.product)}</strong>`);
            }
            if (priority) {
                meta.push(`<span class="badge ${level}">${esc(priority)}</span>`);
            }
            if (item.type) {
                meta.push(`<span class="badge ok">${esc(item.type)}</span>`);
            }

            const body =
                item.message ||
                item.recommendation ||
                item.explanation ||
                item.description ||
                item.insight ||
                "";

            card.innerHTML = `
                <div class="note-meta">${meta.join("")}</div>
                <p>${esc(body)}</p>
            `;
        }

        container.appendChild(card);
    });
}

async function loadInsights() {
    const data = await apiGet("/api/dashboard/insights");
    renderNoteCards($id("insightsContainer"), data.insights || [], "insights");
    showSection("section-insights");
}

async function loadRecommendations() {
    const data = await apiGet("/api/dashboard/recommendations");
    renderNoteCards(
        $id("recommendationsContainer"),
        data.recommendations || [],
        "recommendations"
    );
    showSection("section-decisions");
}

async function loadAnomalies() {
    const data = await apiGet("/api/dashboard/anomalies");
    const anomalies = data.anomalies || [];

    const summary = $id("anomaliesSummary");
    if (summary) {
        if (!anomalies.length) {
            summary.innerHTML = `<span class="badge ok">No anomalies detected</span>`;
        } else {
            const high = anomalies.filter((item) => item.severity === "High").length;
            summary.innerHTML = `
                <span class="badge high">${anomalies.length} anomaly window${anomalies.length > 1 ? "s" : ""}</span>
                ${high ? `<span class="badge high">${high} high severity</span>` : ""}
                <span class="badge medium">robust z-score ≥ 3.0</span>
            `;
        }
    }

    renderNoteCards($id("anomaliesContainer"), anomalies, "anomalies");
    showSection("section-anomalies");
}

async function loadMLDecisions() {
    const data = await apiGet("/api/decision");
    renderNoteCards(
        $id("mlRecommendationsContainer"),
        data.recommendations || [],
        "AI recommendations"
    );
    showSection("section-ai");
}

async function loadForecast() {
    const data = await apiGet("/api/forecast");
    const body = $id("forecastBody");
    if (!body) return;

    body.innerHTML = "";
    const forecasts = data.forecast || [];

    if (!forecasts.length) {
        body.innerHTML = `<tr><td colspan="6" class="muted-cell">No forecast rows were generated.</td></tr>`;
    }

    forecasts.forEach((item) => {
        const current = Number(item.Current_Weekly_Demand);
        const predicted = Number(item.Predicted_Next_Week);
        const change = Number(item.Demand_Change);
        const changePercent = Number(item.Demand_Change_Percent);

        const trendClass = change > 0 ? "positive" : change < 0 ? "negative" : "";
        const arrow = change > 0 ? "▲" : change < 0 ? "▼" : "→";
        const sign = change >= 0 ? "+" : "";

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${esc(item.Product || "—")}</td>
            <td class="num">${fmtNumber(current)}</td>
            <td class="num">${fmtNumber(predicted)}</td>
            <td class="num ${trendClass}">${sign}${change.toFixed(2)}</td>
            <td class="num ${trendClass}">${sign}${changePercent.toFixed(2)}%</td>
            <td class="${trendClass}">${arrow} ${esc(item.Trend || "Stable")}</td>
        `;
        body.appendChild(row);
    });

    showSection("section-forecast");
}

async function loadModelPerformance() {
    const data = await apiGet("/api/model-performance");
    state.validation = data;

    const metrics = data.metrics || {};

    setText("mlModel", data.model || "—");
    setText("trainingWeeks", data.training_weeks ?? "—");
    setText("testingWeeks", data.testing_weeks ?? "—");
    setText("modelMAE", metrics.mae !== undefined ? Number(metrics.mae).toFixed(2) : "—");
    setText("modelRMSE", metrics.rmse !== undefined ? Number(metrics.rmse).toFixed(2) : "—");
    setText("modelR2", metrics.r2 !== undefined ? Number(metrics.r2).toFixed(2) : "—");
    setText("modelMAPE", metrics.mape !== undefined && metrics.mape !== null ? `${Number(metrics.mape).toFixed(1)}%` : "—");

    const overviewR2 = $id("overviewModelR2");
    if (overviewR2 && metrics.r2 !== undefined) {
        overviewR2.textContent = Number(metrics.r2).toFixed(2);
    }

    const description = $id("modelPerformanceDescription");
    if (description) {
        description.textContent =
            `Time-based backtest of the ${data.model || "demand"} model on ` +
            `${data.testing_weeks} unseen testing weeks (trained on ${data.training_weeks}).`;
    }

    renderValidationTable(data);
    renderEvaluationTable(data);
    showSection("section-model", "section-validation", "section-evaluation");
}

function renderValidationTable(data) {
    const body = $id("validationBody");
    if (!body) return;

    const results = (data && data.validation_results) || [];
    body.innerHTML = "";

    const filter = $id("validationProductFilter");
    let selectedProduct = filter ? filter.value : "";

    if (filter) {
        const products = Array.from(new Set(results.map((item) => item.Product))).sort();
        filter.innerHTML = '<option value="">All products</option>';
        products.forEach((product) => {
            const option = document.createElement("option");
            option.value = product;
            option.textContent = product;
            filter.appendChild(option);
        });
        if (selectedProduct && products.includes(selectedProduct)) {
            filter.value = selectedProduct;
        } else {
            selectedProduct = "";
        }
    }

    const rows = results.filter(
        (item) => !selectedProduct || item.Product === selectedProduct
    );

    if (!rows.length) {
        body.innerHTML = `<tr><td colspan="5" class="muted-cell">No validation rows available.</td></tr>`;
        return;
    }

    rows.forEach((item) => {
        const actual = Number(item.Weekly_Quantity);
        const predicted = Number(item.Predicted_Quantity);
        const error = Math.abs(actual - predicted);

        const row = document.createElement("tr");
        if (error > (data.metrics ? data.metrics.mae : 0) * 2) {
            row.className = "row-error";
        }

        row.innerHTML = `
            <td>${fmtDate(item.Week)}</td>
            <td>${esc(item.Product)}</td>
            <td class="num">${actual.toFixed(0)}</td>
            <td class="num">${predicted.toFixed(2)}</td>
            <td class="num"><span class="abs-err">${error.toFixed(2)}</span></td>
        `;
        body.appendChild(row);
    });
}

function renderEvaluationTable(data) {
    const body = $id("evaluationBody");
    if (!body) return;

    const results = (data && data.validation_results) || [];
    const products = {};

    results.forEach((item) => {
        if (!products[item.Product]) {
            products[item.Product] = { actual: [], predicted: [] };
        }
        products[item.Product].actual.push(Number(item.Weekly_Quantity));
        products[item.Product].predicted.push(Number(item.Predicted_Quantity));
    });

    body.innerHTML = "";

    Object.keys(products).forEach((product) => {
        const actual = products[product].actual;
        const predicted = products[product].predicted;

        let absoluteError = 0;
        let squaredError = 0;
        let totalVariance = 0;

        const actualMean =
            actual.reduce((sum, value) => sum + value, 0) / actual.length;

        for (let index = 0; index < actual.length; index++) {
            const error = actual[index] - predicted[index];
            absoluteError += Math.abs(error);
            squaredError += error * error;
            totalVariance += Math.pow(actual[index] - actualMean, 2);
        }

        const mae = absoluteError / actual.length;
        const rmse = Math.sqrt(squaredError / actual.length);
        const r2 = totalVariance !== 0 ? 1 - squaredError / totalVariance : 0;

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${esc(product)}</td>
            <td class="num">${mae.toFixed(2)}</td>
            <td class="num">${rmse.toFixed(2)}</td>
            <td class="num ${r2 >= 0 ? "positive" : "negative"}">${r2.toFixed(2)}</td>
        `;
        body.appendChild(row);
    });
}

async function loadInventory() {
    const data = await apiGet("/api/inventory");
    const body = $id("inventoryBody");
    const explanations = $id("inventoryExplanations");
    if (!body) return;

    body.innerHTML = "";

    if (data.safety_buffer) {
        setText("inventoryBufferChip", `Safety buffer ${data.safety_buffer}`);
        const description = $id("inventoryDescription");
        if (description) {
            description.textContent =
                `Recommended stock = predicted weekly demand × (1 + ${data.safety_buffer} safety buffer).`;
        }
    }

    const recommendations = data.recommendations || [];

    if (!recommendations.length) {
        body.innerHTML = `<tr><td colspan="6" class="muted-cell">No inventory recommendations were generated.</td></tr>`;
    }

    recommendations.forEach((item) => {
        const priority = (item.priority || "Low").toLowerCase();
        const changePercent = Number(item.demand_change_percent);

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${esc(item.product)}</td>
            <td class="num">${fmtNumber(item.current_demand)}</td>
            <td class="num">${fmtNumber(item.predicted_demand)}</td>
            <td class="num"><strong>${fmtNumber(item.recommended_stock)}</strong></td>
            <td>${esc(item.action)}</td>
            <td><span class="pill ${priority}">${esc(item.priority)}</span></td>
        `;
        body.appendChild(row);
    });

    if (explanations) {
        renderNoteCards(explanations, recommendations, "explanations");
    }

    const priorityOrder = { HIGH: 3, MEDIUM: 2, LOW: 1 };
    let topPriority = "—";

    recommendations.forEach((item) => {
        const priority = (item.priority || "").toUpperCase();
        if (topPriority === "—" || (priorityOrder[priority] || 0) > (priorityOrder[topPriority] || 0)) {
            topPriority = priority;
        }
    });

    setText("overviewTopPriority", topPriority);
    showSection("section-inventory");
}

async function loadQuality() {
    const data = await apiGet("/api/dashboard/quality");

    setText("qualityRowsBefore", fmtNumber(data.rows_before));
    setText("qualityRowsAfter", fmtNumber(data.rows_after));
    setText("qualityDuplicates", fmtNumber(data.duplicates_removed));
    setText("qualityMissing", fmtNumber(data.missing_cells));
    setText("qualityCompleteness", `${data.completeness_percent}%`);
    setText("qualityDupFree", `${data.duplicate_free_percent}%`);

    const score = Number(data.quality_score) || 0;

    const gauge = $id("qualityGauge");
    if (gauge) {
        const circumference = 326.7;
        gauge.style.strokeDashoffset = String(circumference * (1 - score / 100));
        gauge.style.stroke =
            score >= 85 ? cssVar("--success") : score >= 60 ? cssVar("--warning") : cssVar("--danger");
    }

    const scoreText = $id("qualityScoreNum");
    if (scoreText) scoreText.textContent = score.toFixed(0);

    const body = $id("qualityBody");
    if (body) {
        body.innerHTML = "";

        (data.columns || []).forEach((column) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${esc(column.name)}</td>
                <td>${esc(column.data_type)}</td>
                <td class="num">${column.missing_values > 0 ? `<span class="abs-err">${column.missing_values}</span>` : "0"}</td>
                <td class="num">${fmtNumber(column.unique_values)}</td>
            `;
            body.appendChild(row);
        });
    }

    showSection("section-quality");
}

async function loadHistory() {
    const data = await apiGet("/api/datasets");
    const body = $id("historyBody");
    if (!body) return;

    body.innerHTML = "";
    const datasets = data.datasets || [];

    if (!datasets.length) {
        body.innerHTML = `<tr><td colspan="6" class="muted-cell">No datasets uploaded yet.</td></tr>`;
        showSection("section-history");
        return;
    }

    datasets.forEach((dataset) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${esc(dataset.file_name)}</td>
            <td>${esc((dataset.file_type || "").toUpperCase())}</td>
            <td class="num">${fmtNumber(dataset.row_count)}</td>
            <td class="num">${fmtNumber(dataset.column_count)}</td>
            <td>${fmtDate(dataset.upload_date)}</td>
            <td><span class="pill low">${esc(dataset.processing_status)}</span></td>
        `;
        body.appendChild(row);
    });

    showSection("section-history");
}

async function loadWorkspace() {
    await loadDashboardData();
    await Promise.all([
        loadInsights(),
        loadRecommendations(),
        loadAnomalies(),
        loadQuality(),
        loadAnalytics(),
        loadForecast(),
        loadModelPerformance(),
        loadMLDecisions(),
        loadInventory()
    ]);
    await loadHistory().catch(() => {});
}

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initSidebar();
    initUpload();
    chartEmptyStyle();

    $id("refreshHistoryBtn")?.addEventListener("click", () => {
        loadHistory().catch((error) => showToast(error.message, "error"));
    });

    $id("exportReportBtn")?.addEventListener("click", () => {
        window.open("/api/system/report", "_blank");
    });

    $id("downloadReportLink")?.addEventListener("click", (event) => {
        event.preventDefault();
        window.open("/api/system/report", "_blank");
    });

    $id("toggleStaticBtn")?.addEventListener("click", (event) => {
        const wrap = $id("staticChartsWrap");
        if (!wrap) return;
        wrap.classList.toggle("is-hidden");
        event.target.textContent = wrap.classList.contains("is-hidden")
            ? "Static Charts"
            : "Hide Static Charts";
    });

    $id("validationProductFilter")?.addEventListener("change", () => {
        if (state.validation) renderValidationTable(state.validation);
    });

    loadHealth();
    loadHistory().catch(() => {});
});
