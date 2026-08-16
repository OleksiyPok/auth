# app/infrastructure/email/registry.py

from app.infrastructure.email.providers.dummy import DummyEmailService
from app.infrastructure.email.providers.mailjet import MailjetEmailService
from app.infrastructure.email.providers.mailtrap import MailtrapEmailService

EMAIL_PROVIDERS = {
    "mailtrap": MailtrapEmailService,
    "mailjet": MailjetEmailService,
    "dummy": DummyEmailService,
}
