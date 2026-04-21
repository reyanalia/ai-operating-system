from datetime import datetime


class DocumentTool:
    """
    Document generation tool — proposals, social posts, email campaigns,
    content calendars, and blog posts.
    """

    def __init__(self) -> None:
        self._documents: dict[str, dict] = {}

    # ── Proposal ─────────────────────────────────────────────────────────────

    def create_proposal(
        self,
        prospect_name: str,
        prospect_company: str,
        pain_points: list[str],
        pricing_tier: str,
        business_name: str = "",
        value_proposition: str = "",
        proposed_solution: str = "",
        custom_notes: str = "",
        lead_id: str = "",
    ) -> dict:
        pricing = {
            "starter": {
                "price": "$499/mo",
                "users": "up to 10",
                "features": ["Core project management", "Basic reporting", "Email support"],
            },
            "professional": {
                "price": "$999/mo",
                "users": "up to 50",
                "features": [
                    "Advanced automation",
                    "Custom dashboards",
                    "Priority support",
                    "API access",
                ],
            },
            "enterprise": {
                "price": "Custom pricing",
                "users": "Unlimited",
                "features": [
                    "Full customization",
                    "Dedicated CSM",
                    "SLA guarantees",
                    "On-premise option",
                    "SSO / SAML",
                ],
            },
        }

        tier = pricing.get(pricing_tier, pricing["professional"])
        pain_list = "\n".join(f"  • {p}" for p in pain_points)
        feature_list = "\n".join(f"  ✓ {f}" for f in tier["features"])
        date_str = datetime.now().strftime("%B %d, %Y")

        content = f"""
{'═' * 54}
        PROPOSAL FOR {prospect_company.upper()}
          Prepared by {business_name}
               {date_str}
{'═' * 54}

Dear {prospect_name},

Thank you for your interest in {business_name}. Based on our
conversations, I've prepared this proposal addressing your
specific needs.

── EXECUTIVE SUMMARY ─────────────────────────────────────
{value_proposition}

We understand that {prospect_company} is currently experiencing:
{pain_list}

This proposal outlines how {business_name} resolves these
challenges with measurable ROI within 90 days.

── PROPOSED SOLUTION ─────────────────────────────────────
{proposed_solution or f'Our {pricing_tier.capitalize()} platform provides a complete, configured solution.'}

── INVESTMENT ────────────────────────────────────────────
  Plan    : {pricing_tier.capitalize()}
  Price   : {tier['price']}
  Users   : {tier['users']}

  Included:
{feature_list}

── EXPECTED OUTCOMES ─────────────────────────────────────
  • 10+ hours/week saved on coordination
  • 40% reduction in status-meeting overhead
  • Real-time project visibility across all teams
  • ROI-positive within 60 days

── NEXT STEPS ────────────────────────────────────────────
  1. Review this proposal
  2. 30-min Q&A call this week
  3. 14-day free trial
  4. Contract & onboarding kickoff
{f'{chr(10)}  Note: {custom_notes}' if custom_notes else ''}

Ready to move forward? Reply to this email or book directly:
calendly.com/{business_name.lower().replace(' ', '')}/next-steps

Best regards,
{business_name} Sales Team
{'═' * 54}
"""

        slug = prospect_company.lower().replace(" ", "_")
        doc_id = f"proposal_{lead_id or slug}_{datetime.now().strftime('%Y%m%d')}"
        self._documents[doc_id] = {
            "id": doc_id,
            "type": "proposal",
            "content": content,
            "created_at": datetime.now().isoformat(),
        }

        return {
            "success": True,
            "document_id": doc_id,
            "proposal_content": content,
            "pricing_tier": pricing_tier,
            "price": tier["price"],
        }

    # ── Content repurposing ───────────────────────────────────────────────────

    def repurpose_content(
        self,
        source_content: str,
        source_type: str,
        target_channels: list[str],
        brand_voice: str = "",
        tone_override: str = "",
    ) -> dict:
        voice = tone_override or brand_voice
        char_limits = {
            "twitter": 280,
            "linkedin": 3000,
            "instagram": 2200,
            "email": 5000,
            "blog": 10_000,
            "newsletter": 4000,
        }

        results: dict[str, dict] = {}
        snippet = source_content[:200].rstrip()

        for ch in target_channels:
            limit = char_limits.get(ch, 2000)
            if ch == "twitter":
                results[ch] = {
                    "content": f"[Twitter/X | {voice} | max 280 chars]\n\n{snippet}…\n\n#B2BSaaS #Productivity",
                    "char_limit": limit,
                    "format": "tweet or thread",
                }
            elif ch == "linkedin":
                results[ch] = {
                    "content": (
                        f"[LinkedIn | {voice}]\n\n{source_content[:500]}\n\n"
                        "Key takeaways:\n• Insight 1\n• Insight 2\n• Insight 3\n\n"
                        "What has your experience been? Drop a comment below. 👇"
                    ),
                    "char_limit": limit,
                    "format": "long-form post with engagement hook",
                }
            elif ch == "email":
                results[ch] = {
                    "content": (
                        f"[Email | {voice}]\n\nSubject: {snippet[:60]}…\n\n"
                        f"{source_content[:800]}\n\n[CTA Button]"
                    ),
                    "char_limit": limit,
                    "format": "newsletter / nurture email",
                }
            elif ch == "blog":
                results[ch] = {
                    "content": (
                        f"[Blog Post | {voice}]\n\nTitle: Expanding on: {source_type}\n\n"
                        f"{source_content}\n\n"
                        "[Add: intro, 3–5 H2 sections, conclusion, CTA]"
                    ),
                    "char_limit": limit,
                    "format": "long-form SEO article",
                }
            else:
                results[ch] = {
                    "content": f"[{ch.capitalize()} | {voice}]\n\n{snippet}…",
                    "char_limit": limit,
                    "format": "standard post",
                }

        return {
            "success": True,
            "repurposed_content": results,
            "channels_count": len(target_channels),
            "source_type": source_type,
        }

    # ── Social posts ──────────────────────────────────────────────────────────

    def create_social_post(
        self,
        platform: str,
        topic: str,
        key_message: str,
        brand_voice: str = "",
        company: str = "",
        include_cta: bool = True,
        hashtags: list[str] | None = None,
    ) -> dict:
        tags = " ".join(f"#{h}" for h in (hashtags or []))
        cta = "\n\n→ Learn more at our website" if include_cta else ""
        templates = {
            "linkedin": f"💡 {topic}\n\n{key_message}\n\nAt {company}, we've seen this firsthand.{cta}\n\n{tags}",
            "twitter": f"{key_message[:200]}{cta[:60]}\n\n{tags}",
            "instagram": f"{topic} ✨\n\n{key_message}\n\n{tags}",
            "facebook": f"{topic}\n\n{key_message}{cta}\n\n{tags}",
        }
        post = templates.get(platform, templates["linkedin"])
        return {
            "success": True,
            "platform": platform,
            "post": post,
            "brand_voice": brand_voice,
            "char_count": len(post),
        }

    # ── Email campaigns ───────────────────────────────────────────────────────

    def create_email_campaign(
        self,
        campaign_goal: str,
        target_segment: str,
        num_emails: int,
        company: str = "",
        value_proposition: str = "",
        sequence_days: list[int] | None = None,
        key_offer: str = "",
    ) -> dict:
        days = (sequence_days or [1, 3, 7, 14, 21, 30])[:num_emails]
        email_types = [
            "Welcome / Intro",
            "Value / Education",
            "Social proof",
            "Offer / CTA",
            "Follow-up / Last chance",
        ]

        emails = [
            {
                "email_number": i + 1,
                "send_day": days[i] if i < len(days) else days[-1] + (i - len(days) + 1) * 7,
                "type": email_types[i % len(email_types)],
                "subject": f"Email {i + 1}: {campaign_goal[:50]}",
                "preview_text": f"Helping {target_segment} achieve their goals…",
                "key_content": value_proposition if i == 0 else f"Nurturing toward: {campaign_goal}",
                "cta": key_offer or "Schedule a free demo",
            }
            for i in range(num_emails)
        ]

        return {
            "success": True,
            "campaign": {
                "goal": campaign_goal,
                "target_segment": target_segment,
                "total_emails": num_emails,
                "emails": emails,
                "estimated_duration_days": days[-1] if days else 21,
            },
        }

    # ── Content calendar ──────────────────────────────────────────────────────

    def create_content_calendar(
        self,
        period: str,
        channels: list[str],
        company: str = "",
        themes: list[str] | None = None,
        posts_per_week: int = 3,
    ) -> dict:
        weeks_map = {"week": 1, "month": 4, "quarter": 13}
        num_weeks = weeks_map.get(period, 4)
        default_themes = themes or [
            "Thought leadership",
            "Product tips",
            "Customer success story",
            "Industry insights",
            "Behind the scenes",
        ]

        posts = []
        for week in range(1, num_weeks + 1):
            for i, channel in enumerate(channels[:posts_per_week]):
                theme = default_themes[(week + i) % len(default_themes)]
                posts.append(
                    {
                        "week": week,
                        "channel": channel,
                        "theme": theme,
                        "content_type": (
                            "Post" if channel in ("twitter", "linkedin", "instagram")
                            else "Article" if channel == "blog"
                            else "Email"
                        ),
                        "status": "planned",
                    }
                )

        return {
            "success": True,
            "calendar": {
                "period": period,
                "total_posts": len(posts),
                "posts_per_week": posts_per_week,
                "channels": channels,
                "posts": posts,
            },
        }

    # ── Blog posts ────────────────────────────────────────────────────────────

    def write_blog_post(
        self,
        title: str,
        target_keyword: str,
        company: str = "",
        industry: str = "",
        outline: list[str] | None = None,
        word_count: int = 1200,
        audience: str = "",
    ) -> dict:
        default_outline = outline or [
            "Introduction: The Problem",
            f"Why {target_keyword} Matters in {industry or 'Your Industry'}",
            "Common Mistakes to Avoid",
            "Best Practices & Proven Solutions",
            f"Real-World Example: How {company or 'Leading Teams'} Did It",
            "Conclusion & Next Steps",
        ]

        return {
            "success": True,
            "blog_post": {
                "title": title,
                "target_keyword": target_keyword,
                "audience": audience,
                "word_count_target": word_count,
                "estimated_read_time": f"{word_count // 200} min read",
                "outline": default_outline,
                "meta_description": (
                    f"Learn how {target_keyword} transforms {industry} teams. "
                    f"Actionable insights from {company}."
                ),
                "status": "outline_ready",
            },
        }
