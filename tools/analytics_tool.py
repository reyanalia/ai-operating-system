import random
from datetime import datetime


class AnalyticsTool:
    """
    Analytics tool adapter — KPI data, reporting, and churn detection.

    Mock implementation with realistic sample data.
    Swap out for real data warehouse / BI tool calls when ready.
    """

    def __init__(self) -> None:
        self._kpi_store = {
            "MRR": {"current": 125_400, "previous": 118_200, "unit": "$", "trend": "+6.1%"},
            "ARR": {"current": 1_504_800, "previous": 1_418_400, "unit": "$", "trend": "+6.1%"},
            "churn_rate": {"current": 2.3, "previous": 2.8, "unit": "%", "trend": "-0.5pp"},
            "NPS": {"current": 47, "previous": 42, "unit": "score", "trend": "+5"},
            "ticket_resolution_time": {"current": 4.2, "previous": 5.1, "unit": "hrs", "trend": "-18%"},
            "CAC": {"current": 1_850, "previous": 2_100, "unit": "$", "trend": "-11.9%"},
            "LTV": {"current": 24_600, "previous": 22_800, "unit": "$", "trend": "+7.9%"},
            "active_users": {"current": 1_247, "previous": 1_103, "unit": "users", "trend": "+13.1%"},
            "conversion_rate": {"current": 3.8, "previous": 3.2, "unit": "%", "trend": "+0.6pp"},
        }

    def get_kpi_data(self, metrics: list[str], period: str = "month") -> dict:
        results = {}
        for metric in metrics:
            if metric in self._kpi_store:
                results[metric] = self._kpi_store[metric]
            else:
                results[metric] = {"current": "N/A", "unit": "", "trend": "No data"}
        return {
            "period": period,
            "as_of": datetime.now().strftime("%Y-%m-%d"),
            "metrics": results,
        }

    def generate_report(
        self,
        report_type: str,
        metrics: list[str],
        period_start: str = "",
        period_end: str = "",
        format: str = "summary",
    ) -> dict:
        kpi_data = self.get_kpi_data(metrics)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            "=" * 52,
            f"  {report_type.upper()} REPORT",
            f"  Period : {period_start or 'Last period'} → {period_end or 'Today'}",
            f"  Generated : {now_str}",
            "=" * 52,
            "",
            "KEY METRICS",
            "-" * 30,
        ]

        for metric, data in kpi_data["metrics"].items():
            if isinstance(data, dict) and "current" in data:
                unit = data.get("unit", "")
                val = data["current"]
                trend = data.get("trend", "")
                prefix = unit if unit == "$" else ""
                suffix = f" {unit}" if unit not in ("$", "") else ""
                lines.append(f"  {metric:<28} {prefix}{val}{suffix}  ({trend})")

        if format in ("detailed", "executive"):
            lines += [
                "",
                "HIGHLIGHTS",
                "-" * 30,
                "  • MRR growing above target — maintain acquisition pace",
                "  • Churn improved — CS team interventions working",
                "  • NPS at 47 — healthy but room to reach 60+",
            ]

        if format == "executive":
            lines += [
                "",
                "RECOMMENDATION",
                "-" * 30,
                "  Increase investment in top-performing acquisition channels.",
                "  Continue at-risk customer program — churn trend is positive.",
            ]

        lines.append("=" * 52)

        return {
            "success": True,
            "report": "\n".join(lines),
            "report_type": report_type,
            "metrics_covered": metrics,
            "format": format,
        }

    def analyze_content(
        self, channel: str, period: str, metrics: list[str] | None = None
    ) -> dict:
        mock = {
            "linkedin": {
                "impressions": 12_500,
                "clicks": 340,
                "engagement_rate": "4.2%",
                "followers_gained": 89,
            },
            "twitter": {
                "impressions": 8_900,
                "clicks": 120,
                "engagement_rate": "2.8%",
                "new_followers": 34,
            },
            "email": {
                "open_rate": "28.4%",
                "click_rate": "4.1%",
                "unsubscribes": 12,
                "deliverability": "98.2%",
            },
            "blog": {
                "pageviews": 3_400,
                "avg_time_on_page": "3:42",
                "bounce_rate": "61%",
                "organic_traffic": 1_890,
            },
        }
        return {
            "channel": channel,
            "period": period,
            "performance": mock.get(channel, {"data": "No data available"}),
            "top_content": f"Best-performing post on {channel} this {period}",
            "recommendations": [
                f"Increase posting frequency on {channel}",
                "A/B test headline formats",
                "Engage with comments in the first 60 minutes after posting",
            ],
        }

    def flag_at_risk(
        self, threshold: str = "medium", period_days: int = 30
    ) -> dict:
        count_map = {"low": 1, "medium": 3, "high": 5}
        count = count_map.get(threshold, 3)
        reasons = ["Low usage", "Open support tickets", "NPS drop", "Champion left company"]

        customers = [
            {
                "customer": f"Customer {i + 1}",
                "risk_score": random.randint(60, 90),
                "last_login_days_ago": random.randint(14, period_days),
                "reason": reasons[i % len(reasons)],
                "recommended_action": "Schedule check-in call within 48 hours",
                "arr_at_risk": f"${random.randint(10_000, 50_000):,}",
            }
            for i in range(count)
        ]

        total_arr = sum(int(c["arr_at_risk"].replace("$", "").replace(",", "")) for c in customers)
        return {
            "threshold": threshold,
            "period_days": period_days,
            "at_risk_count": len(customers),
            "customers": customers,
            "total_arr_at_risk": f"${total_arr:,}",
        }
