# Changelog — SBI-ADS

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] — Professional Edition

### Added
- **Sidebar workspace UI** with section navigation, scroll-spy highlighting, mobile drawer, and collapsible layout — replacing the single-scroll page.
- **Dark / light theme system** (CSS design tokens, persisted in `localStorage`, respects OS preference).
- **Interactive analytics** — Chart.js visualizations (revenue/quantity trend, top products, regional doughnut, category polar, price histogram, HTML correlation matrix) backed by the new `GET /api/dashboard/analytics` endpoint. Static PNG charts remain available behind a toggle.
- **Anomaly Radar** — new `analytics/anomaly_detector.py` detects abnormal weekly demand using the robust z-score (median/MAD, resistant to outliers); surfaced via `GET /api/dashboard/anomalies` with severity grading.
- **Data-quality governance** — new `GET /api/dashboard/quality` endpoint with a documented quality score (70% completeness + 30% duplicate-free), missing-cell totals and per-column report, plus an SVG gauge in the UI.
- **MAPE** added to model metrics; model name now read from the actual fitted estimator instead of a hard-coded label.
- **Per-product backtest filter** on the validation table.
- **System endpoints** — `GET /api/system/health` (version, uptime, database probe) and `GET /api/system/report` (downloadable JSON analysis report), plus a live health pill in the top bar.
- **Toast notifications** and a staged **analysis pipeline tracker** (Upload → KPIs → Analytics → ML Forecast → Decisions → Inventory).
- **Drag-and-drop upload** with client-side file selection state.
- **Zero-config SQLite database** (`database/connection.py` rewritten as a dual-driver layer with auto-created schema); MySQL still fully supported and documented via `database/schema.sql`.
- **`core/config.py`** — central, environment-driven configuration with `.env` support and `.env.example` template.
- **`backend/shared.py`** — shared request helpers; every router now returns consistent, actionable HTTP errors (404/410/413/422/500).
- **Upload hardening** — size limit enforcement before disk write, empty-file rejection, atomic analysis-artefact writes, original filenames no longer touch the filesystem.
- **KPI upgrades** — average order value, analysis period, top-product revenue share, top category.
- **One-command launchers** (`run.sh`, `run.bat`) and a favicon.

### Changed
- Full UI redesign: professional design system (Indigo/Cyan palette, soft shadows, consistent radii), KPI cards with icons, priority pills, and dark-mode-ready chart theming.
- Static charts rebranded (horizontal top-product bars, median marker, 7-day rolling-average overlay, fixed −1..1 correlation scale) with the same filenames as v1.
- Cleaning pipeline hardens against `"nan"` string artefacts and non-string headers; fails fast when no usable rows remain.
- Anomaly detection in the pipeline now receives the raw upload's own column mapping (more robust for unusual column layouts).
- Revenue KPIs prefer `quantity × price`, with graceful fallback to an explicit revenue column.
- `requirements.txt` pinned with minimum versions; `python-dotenv` added; MySQL driver documented as optional.

### Fixed
- Hard-coded `Linear Regression` label on the model-performance card (now reflects the real fitted model).
- Missing error handling when a stored dataset file was deleted server-side (now HTTP 410 with a clear message).
- Duplicate recommendation rendering and repeated `/api/decision` calls in the UI flow.
- Analysis JSON persisted non-atomically (crash risk mid-write).

### Removed
- Compiled `__pycache__` artefacts from the repository.
- Dead empty module `ml/model_evaluation.py`.

## [1.0.0] — Initial release

- FastAPI backend, upload + analysis pipeline (profile, clean, KPIs, EDA, static charts, insights, recommendations).
- Weekly demand forecasting with lag/rolling features, backtesting, model performance endpoint.
- ML decision support and inventory intelligence modules.
- MySQL-backed dataset history and vanilla JS dashboard.
