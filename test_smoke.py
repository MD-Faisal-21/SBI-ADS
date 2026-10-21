import io
import sys

from fastapi.testclient import TestClient

import main

_client_context = TestClient(main.app, follow_redirects=True)
client = _client_context.__enter__()
failures = []


def check(name, response, expect=200):
    ok = response.status_code == expect
    print(f"{'PASS' if ok else 'FAIL'}  {name:42s} -> {response.status_code}")
    if not ok:
        failures.append((name, response.status_code, response.text[:400]))

check("GET / (redirect to dashboard)", client.get("/"))
check("GET /dashboard (UI page)", client.get("/dashboard"))
health = client.get("/api/system/health")
check("GET /api/system/health", health)
print("    health payload:", health.json())

with open("data/ml_sales_data.csv", "rb") as handle:
    upload = client.post(
        "/api/upload",
        files={"file": ("ml_sales_data.csv", handle.read(), "text/csv")},
    )
check("POST /api/upload (full pipeline)", upload)

if upload.status_code == 200:
    analysis = upload.json()["analysis"]
    print("    profile:", analysis["profile"]["rows"], "rows /",
          analysis["profile"]["columns"], "cols")
    print("    kpis:", {k: analysis["kpis"].get(k) for k in
          ("total_revenue", "total_quantity", "total_products", "top_product")})
    print("    insights:", len(analysis["insights"]),
          "| recommendations:", len(analysis["recommendations"]),
          "| anomalies:", len(analysis["anomalies"]))

for endpoint in [
    "/api/dashboard",
    "/api/dashboard/insights",
    "/api/dashboard/recommendations",
    "/api/dashboard/anomalies",
    "/api/dashboard/analytics",
    "/api/dashboard/quality",
    "/api/forecast",
    "/api/decision",
    "/api/model-performance",
    "/api/inventory",
    "/api/datasets",
    "/api/system/report",
]:
    check(f"GET {endpoint}", client.get(endpoint))

forecast = client.get("/api/forecast")
if forecast.status_code == 200:
    rows = forecast.json()["forecast"]
    assert rows, "forecast returned zero rows"
    print("    forecast sample:", rows[0])

perf = client.get("/api/model-performance")
if perf.status_code == 200:
    body = perf.json()
    print("    model:", body["model"], "| metrics:", body["metrics"])
    assert body["metrics"]["r2"] is not None

quality = client.get("/api/dashboard/quality")
if quality.status_code == 200:
    print("    quality score:", quality.json()["quality_score"])

anomalies = client.get("/api/dashboard/anomalies")
if anomalies.status_code == 200:
    print("    anomalies found:", len(anomalies.json()["anomalies"]))

with io.BytesIO(b"not,a,real\ndate,dataset,here\n") as bogus:
    bad = client.post(
        "/api/upload",
        files={"file": ("bogus.csv", bogus.read(), "text/csv")},
    )
ok = bad.status_code < 500
print(f"{'PASS' if ok else 'FAIL'}  bogus upload handled gracefully        -> {bad.status_code}")
if not ok:
    failures.append(("bogus upload", bad.status_code, bad.text[:300]))

print()
if failures:
    print(f"SMOKE TEST FAILURES: {len(failures)}")
    for name, code, text in failures:
        print(f"  - {name}: {code}\n    {text}")
    sys.exit(1)

print("ALL SMOKE TESTS PASSED ✓")
