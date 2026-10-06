from celery import Celery
from asgiref.sync import async_to_sync
from src.core.mail import mail, create_message
import asyncio

c_app = Celery("worker")

c_app.config_from_object("src.core.config")


@c_app.task(name="src.celery_task.send_mail")
def send_mail(recipients: list[str], subject: str, body: str):

    message = create_message(
        recipients=recipients,
        subject=subject,
        body=body,
    )

    async def send():        
        await asyncio.wait_for(
            mail.send_message(message),
            timeout=30,
        )

    asyncio.run(send())

    return {
        "status": True,
        "message": "E-mail sent successfully."
    }
