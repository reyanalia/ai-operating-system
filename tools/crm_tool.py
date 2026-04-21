import uuid
from datetime import datetime


class CRMTool:
    """
    CRM tool adapter.

    Mock implementation — swap provider string for HubSpot/Salesforce
    and replace method bodies with real API calls. Interface stays identical.
    """

    def __init__(self, provider: str = "mock") -> None:
        self.provider = provider
        self._leads: dict[str, dict] = {}
        self._onboarding_plans: dict[str, dict] = {}
        self._seed_data()

    def _seed_data(self) -> None:
        samples = [
            {
                "name": "Sarah Chen",
                "company": "TechFlow Inc",
                "email": "sarah@techflow.io",
                "company_size": "120 employees",
                "status": "qualified",
                "pain_points": ["manual processes", "spreadsheet chaos"],
                "source": "inbound",
            },
            {
                "name": "Marcus Rivera",
                "company": "Apex Solutions",
                "email": "m.rivera@apex.co",
                "company_size": "350 employees",
                "status": "new",
                "pain_points": ["team coordination", "reporting overhead"],
                "source": "referral",
            },
            {
                "name": "Priya Patel",
                "company": "DataBridge",
                "email": "priya@databridge.com",
                "company_size": "75 employees",
                "status": "proposal_sent",
                "pain_points": ["reporting overhead", "manual processes"],
                "source": "outbound",
            },
        ]
        for data in samples:
            lead_id = str(uuid.uuid4())[:8]
            self._leads[lead_id] = {
                "id": lead_id,
                **data,
                "created_at": datetime.now().isoformat(),
            }

    # ── Lead operations ──────────────────────────────────────────────────────

    def search_leads(self, query: str, status: str = "all") -> dict:
        results = []
        for lead in self._leads.values():
            matches_query = (
                query == "*"
                or query.lower() in lead.get("name", "").lower()
                or query.lower() in lead.get("company", "").lower()
                or query.lower() in lead.get("email", "").lower()
            )
            matches_status = status == "all" or lead.get("status") == status
            if matches_query and matches_status:
                results.append(lead)
        return {"leads": results, "total": len(results), "provider": self.provider}

    def create_lead(
        self,
        name: str,
        company: str,
        email: str,
        phone: str = "",
        company_size: str = "",
        pain_points: list | None = None,
        source: str = "manual",
    ) -> dict:
        lead_id = str(uuid.uuid4())[:8]
        lead = {
            "id": lead_id,
            "name": name,
            "company": company,
            "email": email,
            "phone": phone,
            "company_size": company_size,
            "pain_points": pain_points or [],
            "source": source,
            "status": "new",
            "created_at": datetime.now().isoformat(),
        }
        self._leads[lead_id] = lead
        return {"success": True, "lead": lead, "message": f"Lead created — ID: {lead_id}"}

    def update_lead_status(
        self, lead_id: str, status: str, notes: str = ""
    ) -> dict:
        # Support partial name/company match when full ID isn't known
        if lead_id not in self._leads:
            for lid, lead in self._leads.items():
                if lead_id.lower() in lead.get("name", "").lower() or lead_id.lower() in lead.get("company", "").lower():
                    lead_id = lid
                    break

        if lead_id in self._leads:
            self._leads[lead_id]["status"] = status
            self._leads[lead_id]["last_updated"] = datetime.now().isoformat()
            if notes:
                self._leads[lead_id]["notes"] = notes
            return {"success": True, "lead_id": lead_id, "new_status": status}
        return {"success": False, "error": f"Lead '{lead_id}' not found"}

    def score_lead(
        self,
        lead_id: str,
        company_size: str = "",
        budget: str = "",
        timeline: str = "",
        pain_points: list | None = None,
    ) -> dict:
        score = 0
        breakdown = []

        if company_size:
            digits = "".join(filter(str.isdigit, company_size))
            if digits:
                n = int(digits)
                if 50 <= n <= 500:
                    score += 30
                    breakdown.append("Company size: ideal fit (+30)")
                elif n < 50:
                    score += 10
                    breakdown.append("Company size: too small (+10)")
                else:
                    score += 20
                    breakdown.append("Company size: large enterprise (+20)")

        if budget:
            score += 25
            breakdown.append(f"Budget disclosed: {budget} (+25)")

        if timeline:
            urgent = any(w in timeline.lower() for w in ("immediate", "asap", "this quarter", "urgent"))
            score += 25 if urgent else 10
            breakdown.append(f"Timeline: {timeline} (+{25 if urgent else 10})")

        if pain_points:
            pts = min(len(pain_points) * 5, 20)
            score += pts
            breakdown.append(f"{len(pain_points)} pain points identified (+{pts})")

        grade = "A" if score >= 70 else "B" if score >= 50 else "C" if score >= 30 else "D"
        return {
            "lead_id": lead_id,
            "score": score,
            "grade": grade,
            "breakdown": breakdown,
            "recommendation": (
                "Prioritize — send proposal now"
                if grade == "A"
                else "Nurture — schedule discovery call"
                if grade == "B"
                else "Qualify further before investing"
            ),
        }

    def get_pipeline_summary(self, period: str = "month") -> dict:
        status_counts: dict[str, int] = {}
        for lead in self._leads.values():
            s = lead.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1

        return {
            "period": period,
            "total_leads": len(self._leads),
            "pipeline_by_stage": status_counts,
            "estimated_pipeline_value": f"${len(self._leads) * 25_000:,}",
            "avg_deal_size": "$18,500",
            "close_rate": "23%",
            "provider": self.provider,
        }

    # ── Onboarding operations ─────────────────────────────────────────────────

    def create_onboarding_plan(
        self,
        customer_name: str,
        customer_company: str,
        plan_type: str,
        start_date: str,
        duration_days: int = 30,
        team_size: int | None = None,
        primary_goals: list | None = None,
    ) -> dict:
        milestones_map = {
            "standard": [
                {"day": 1, "name": "Kickoff call", "owner": "CSM"},
                {"day": 3, "name": "Account setup & integrations", "owner": "Customer"},
                {"day": 7, "name": "First users trained", "owner": "CSM"},
                {"day": 14, "name": "First workflow live", "owner": "Customer"},
                {"day": 21, "name": "Check-in & optimization", "owner": "CSM"},
                {"day": 30, "name": "Success review & expansion discussion", "owner": "CSM"},
            ],
            "enterprise": [
                {"day": 1, "name": "Executive kickoff", "owner": "AE + CSM"},
                {"day": 3, "name": "Technical discovery", "owner": "Solutions Engineer"},
                {"day": 7, "name": "Custom integration setup", "owner": "Engineering"},
                {"day": 14, "name": "Pilot user training", "owner": "CSM"},
                {"day": 21, "name": "Pilot review & feedback", "owner": "CSM"},
                {"day": 30, "name": "Broader rollout planning", "owner": "Customer Success"},
                {"day": 45, "name": "Full rollout complete", "owner": "Customer"},
                {"day": 60, "name": "QBR — Quarterly Business Review", "owner": "AE + CSM"},
            ],
            "self-serve": [
                {"day": 1, "name": "Welcome email + setup guide sent", "owner": "Automated"},
                {"day": 3, "name": "Check-in email", "owner": "Automated"},
                {"day": 7, "name": "Usage check + offer call", "owner": "CSM"},
                {"day": 14, "name": "Feature discovery email", "owner": "Automated"},
                {"day": 30, "name": "Success check-in", "owner": "CSM"},
            ],
        }

        plan_id = str(uuid.uuid4())[:8]
        plan = {
            "plan_id": plan_id,
            "customer_name": customer_name,
            "customer_company": customer_company,
            "plan_type": plan_type,
            "start_date": start_date,
            "duration_days": duration_days,
            "team_size": team_size,
            "primary_goals": primary_goals or [],
            "milestones": milestones_map.get(plan_type, milestones_map["standard"]),
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        self._onboarding_plans[plan_id] = plan
        return {"success": True, "plan": plan}

    def track_milestone(
        self,
        customer_id: str,
        milestone: str,
        completion_date: str = "",
        notes: str = "",
    ) -> dict:
        return {
            "success": True,
            "customer_id": customer_id,
            "milestone": milestone,
            "completed_at": completion_date or datetime.now().isoformat(),
            "notes": notes,
        }

    def schedule_call(
        self,
        customer_email: str,
        call_type: str,
        preferred_date: str,
        duration_minutes: int = 60,
    ) -> dict:
        return {
            "success": True,
            "call_type": call_type,
            "customer_email": customer_email,
            "scheduled_date": preferred_date,
            "duration_minutes": duration_minutes,
            "calendar_link": f"https://calendar.example.com/book/{call_type}",
            "confirmation_sent": True,
        }
