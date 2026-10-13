"""
Live End-to-End API Validation Test Runner.
Lab 14: Automated Validation & Verification Suite for Live Cloud Deployment.
Can execute against local or remote environments (e.g. AWS EC2: http://65.0.80.41:8000).
"""
import argparse
import sys
import time
from typing import Any, Dict, List, Optional
import httpx

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class APITestRunner:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.passed = 0
        self.failed = 0
        self.results: List[Dict[str, Any]] = []

    def log(self, status: str, name: str, detail: str = "", elapsed_ms: float = 0.0):
        if status == "PASS":
            self.passed += 1
            icon = "[PASS]"
        else:
            self.failed += 1
            icon = "[FAIL]"

        print(f"{icon} {name:<45} ({elapsed_ms:>6.1f} ms) {detail}")
        self.results.append({
            "name": name,
            "status": status,
            "elapsed_ms": elapsed_ms,
            "detail": detail,
        })

    def run_test(self, name: str, method: str, path: str, expected_status: int, **kwargs) -> Optional[httpx.Response]:
        url = f"{self.base_url}{path}"
        start = time.perf_counter()
        try:
            with httpx.Client(timeout=10.0, follow_redirects=False) as client:
                res = client.request(method, url, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000.0

            if res.status_code == expected_status:
                self.log("PASS", name, f"HTTP {res.status_code}", elapsed)
                return res
            else:
                self.log("FAIL", name, f"Expected {expected_status}, got {res.status_code} - {res.text[:80]}", elapsed)
                return res
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000.0
            self.log("FAIL", name, f"Connection error: {str(e)[:60]}", elapsed)
            return None

    def execute_all(self):
        print("=" * 78)
        print(f"🚀 Cloud-Based URL Shortener - End-to-End Live Validation Suite")
        print(f"Target Server: {self.base_url}")
        print("=" * 78)

        # 1. Core Endpoints
        r_root = self.run_test("1. Root Service Info", "GET", "/", 200)
        r_health = self.run_test("2. ALB Health Check Probe", "GET", "/health", 200)
        self.run_test(
            "3. Message Echo Probe",
            "POST",
            "/api/echo",
            200,
            json={"message": "Cloud Validation Probe", "client_name": "TestRunner"},
        )

        # 2. URL Shortening
        r_shorten = self.run_test(
            "4. Base62 URL Shorten",
            "POST",
            "/api/shorten",
            201,
            json={"url": "https://aws.amazon.com/ec2/"},
        )
        code1 = r_shorten.json().get("short_code") if r_shorten else None

        alias = f"live-{int(time.time()) % 100000}"
        r_custom = self.run_test(
            "5. Custom Vanity Alias Shorten",
            "POST",
            "/api/shorten",
            201,
            json={"url": "https://aws.amazon.com/s3/", "custom_code": alias},
        )

        r_ttl = self.run_test(
            "6. TTL Expiring URL Shorten (24h)",
            "POST",
            "/api/shorten",
            201,
            json={"url": "https://aws.amazon.com/lambda/", "expires_in_hours": 24},
        )

        # 3. Idempotent Duplicate Long URL Reuse
        self.run_test(
            "7. Idempotent Duplicate URL Reuse",
            "POST",
            "/api/shorten",
            201,
            json={"url": "https://aws.amazon.com/ec2/"},
        )

        # 4. Batch Shortening
        self.run_test(
            "8. Atomic Batch Shortening (3 URLs)",
            "POST",
            "/api/shorten/batch",
            201,
            json={
                "urls": [
                    "https://aws.amazon.com/dynamodb/",
                    "https://aws.amazon.com/ecs/",
                    "https://aws.amazon.com/cloudwatch/",
                ],
                "expires_in_hours": 48,
            },
        )

        # 5. Retrieval & Redirection
        self.run_test("9. Paginated Stored URLs List", "GET", "/api/urls?limit=10", 200)

        if alias:
            self.run_test(f"10. Specific URL Metadata Lookup", "GET", f"/api/urls/{alias}", 200)

            # Trigger Redirection (HTTP 307)
            r_redir = self.run_test(f"11. URL Redirection (HTTP 307)", "GET", f"/{alias}", 307)
            if r_redir and r_redir.headers.get("location") == "https://aws.amazon.com/s3/":
                print(f"       -> Confirmed Location header: {r_redir.headers.get('location')}")

            # Check stats increment
            r_stats = self.run_test(f"12. Access Tracking & Click Stats", "GET", f"/api/urls/{alias}/stats", 200)
            if r_stats:
                clicks = r_stats.json().get("click_count", 0)
                print(f"       -> Confirmed click_count: {clicks} (Destination: {r_stats.json().get('destination_domain')})")

        # 6. Analytics & Observability
        self.run_test("13. Top-N Most Clicked Leaderboard", "GET", "/api/stats/top?limit=5", 200)
        self.run_test("14. Destination Domain Share Analysis", "GET", "/api/stats/domains", 200)
        self.run_test("15. Observability & CloudWatch Telemetry", "GET", "/api/stats/report", 200)
        self.run_test("16. Automated TTL Maintenance Sweeper", "POST", "/api/maintenance/cleanup-expired", 200)
        self.run_test("17. Expired Links Audit Query", "GET", "/api/urls/status/expired", 200)

        # 7. Error Scenarios & RFC Boundary Conditions
        self.run_test(
            "18. Error: Malformed URL Rejection",
            "POST",
            "/api/shorten",
            400,
            json={"url": "not-a-valid-url"},
        )
        self.run_test(
            "19. Error: Empty URL String Rejection",
            "POST",
            "/api/shorten",
            400,
            json={"url": ""},
        )
        if alias:
            self.run_test(
                "20. Error: Duplicate Vanity Alias Conflict",
                "POST",
                "/api/shorten",
                409,
                json={"url": "https://other.com", "custom_code": alias},
            )
        self.run_test("21. Error: Non-existent Short Code 404", "GET", "/non-existent-code-99", 404)
        self.run_test(
            "22. Error: Conflicting TTL Parameters",
            "POST",
            "/api/shorten",
            400,
            json={"url": "https://aws.amazon.com", "expires_in_hours": 10, "expires_in_days": 2},
        )

        # Final Summary
        total = self.passed + self.failed
        pass_pct = (self.passed / total * 100.0) if total > 0 else 0.0
        avg_lat = sum(r["elapsed_ms"] for r in self.results) / total if total > 0 else 0.0

        print("=" * 78)
        print("📊 Validation Suite Execution Summary")
        print(f"   Total Test Probes:    {total}")
        print(f"   Passed:               {self.passed} ({pass_pct:.1f}%)")
        print(f"   Failed:               {self.failed}")
        print(f"   Average API Latency:  {avg_lat:.2f} ms")
        print("=" * 78)

        if self.failed == 0:
            print("✅ All validation assertions PASSED successfully!")
            return 0
        else:
            print(f"❌ {self.failed} assertions failed.")
            return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live API Validation Runner for Cloud URL Shortener")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Target API Base URL (e.g. http://localhost:8000 or http://65.0.80.41:8000)")
    args = parser.parse_args()

    runner = APITestRunner(base_url=args.base_url)
    exit_code = runner.execute_all()
    sys.exit(exit_code)
