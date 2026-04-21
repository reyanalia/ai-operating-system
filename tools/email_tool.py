from datetime import datetime


class EmailTool:
    """
    Email tool adapter.

    Mock implementation — swap provider string for Gmail/SendGrid
    and replace method bodies with real API calls. Interface stays identical.
    """

    def __init__(self, provider: str = "mock") -> None:
        self.provider = provider
        self._sent: list[dict] = []

    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        to_name: str = "",
        attach_proposal: bool = False,
    ) -> dict:
        record = {
            "id": f"email_{len(self._sent) + 1:04d}",
            "to": to_email,
            "to_name": to_name,
            "subject": subject,
            "body_preview": body[:200],
            "has_attachment": attach_proposal,
            "sent_at": datetime.now().isoformat(),
            "provider": self.provider,
            "status": "delivered",
        }
        self._sent.append(record)
        return {
            "success": True,
            "email_id": record["id"],
            "message": f"Email delivered to {to_email}",
        }

    def send_report(
        self, report_content: str, recipients: list[str], subject: str
    ) -> dict:
        sent = []
        for addr in recipients:
            result = self.send(to_email=addr, subject=subject, body=report_content)
            sent.append(result)
        return {
            "success": True,
            "sent_count": len(sent),
            "recipients": recipients,
        }

    def get_sent_history(self) -> list[dict]:
        return self._sent
