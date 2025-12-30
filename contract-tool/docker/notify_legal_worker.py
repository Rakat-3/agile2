import os
import smtplib
from email.message import EmailMessage

from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

# IMPORTANT: inside Docker use service names (camunda, mailhog), not localhost
ENGINE_REST = os.getenv("ENGINE_REST", "http://camunda-app:8080/engine-rest")
MAILHOG_HOST = os.getenv("MAILHOG_HOST", "mailhog")
MAILHOG_PORT = int(os.getenv("MAILHOG_PORT", "1025"))
TOPIC_NAME = os.getenv("TOPIC_NAME", "notify-legal")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@local.com")
WORKER_ID = os.getenv("WORKER_ID", "notify-legal-worker")


def send_via_mailhog(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # MailHog: no TLS, no auth
    with smtplib.SMTP(MAILHOG_HOST, MAILHOG_PORT, timeout=10) as s:
        s.send_message(msg)


def handle(task: ExternalTask) -> TaskResult:
    to_email = task.get_variable("toEmail") or "legal@local.com"
    subject = task.get_variable("subject") or "Legal Notification"
    body = task.get_variable("body") or "Please review the contract."

    try:
        send_via_mailhog(to_email, subject, body)
        return task.complete({"emailSent": True})
    except Exception as e:
        return task.handle_failure(
            error_message=str(e),
            error_details=repr(e),
            retries=3,
            retry_timeout=10000
        )


if __name__ == "__main__":
    worker = ExternalTaskWorker(worker_id=WORKER_ID, base_url=ENGINE_REST)
    worker.subscribe(TOPIC_NAME, handle)
    worker.run()
