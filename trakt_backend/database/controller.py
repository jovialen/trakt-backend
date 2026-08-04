from fastapi import APIRouter, HTTPException, Request
from svix.webhooks import Webhook, WebhookVerificationError

from ..settings import SettingsDep
from .service import TenantServiceDep

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/clerk", tags=["Tenants"])
async def clerk_webhook(request: Request, tenants: TenantServiceDep, settings: SettingsDep):
    body = await request.body()
    headers = dict(request.headers)

    try:
        event = Webhook(settings.clerk_webhook_signing_secret).verify(body, headers)
    except WebhookVerificationError as err:
        raise HTTPException(status_code=400, detail="Invalid signature") from err

    event_type = event["type"]
    data = event["data"]

    if event_type == "user.created":
        user_id = data["id"]
        tenants.create(user_id)
    elif event_type == "session.created":
        user_id = data["user_id"]
        tenants.create(user_id)
    elif event_type == "user.deleted":
        user_id = data["id"]
        tenants.delete(user_id)
