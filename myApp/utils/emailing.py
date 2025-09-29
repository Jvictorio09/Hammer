# myApp/utils/emailing.py
from __future__ import annotations
import json
import logging
import requests
from django.conf import settings

log = logging.getLogger(__name__)

class ResendError(RuntimeError):
    pass

def send_email_resend(
    subject: str,
    to: list[str] | tuple[str, ...],
    text: str,
    html: str | None = None,
    reply_to: str | None = None,
    tags: dict[str, str] | None = None,
):
    """
    Sends an email via Resend's /emails endpoint.
    Docs: https://resend.com/docs/api-reference/emails/send-email
    """
    if not settings.RESEND_API_KEY:
        raise ResendError("RESEND_API_KEY is not configured")

    payload = {
        "from": settings.RESEND_FROM,
        "to": list(to),
        "subject": subject,
        "text": text,
    }
    if html:
        payload["html"] = html
    if reply_to or settings.RESEND_REPLY_TO:
        payload["reply_to"] = [reply_to or settings.RESEND_REPLY_TO]
    if tags:
        # Resend “tags” are a list of {"name","value"} objects
        payload["tags"] = [{"name": k, "value": v} for k, v in tags.items()]

    url = f"{settings.RESEND_BASE_URL.rstrip('/')}/emails"
    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
    if resp.status_code >= 400:
        log.error("Resend error (%s): %s", resp.status_code, resp.text)
        raise ResendError(f"Resend failed: {resp.status_code}")

    return resp.json()  # contains id, etc.
