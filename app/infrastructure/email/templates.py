# app/infrastructure/email/templates.py

from string import Template

DRAFT = Template("""Subject: Request Submitted - $request_code - $request_title

Dear $user_name,
....

Best regards,
System
""")

TWO_FACTOR_ENABLED = Template("""
Subject: Two-factor authentication enabled

Two-factor authentication has been successfully enabled for your account.

If you did not perform this action, please secure your account immediately.
""")

TWO_FACTOR_DISABLED = Template("""
Subject: Two-factor authentication disabled

Two-factor authentication has been successfully disabled for your account.

If you did not perform this action, please secure your account immediately.
""")

TEMPLATE_REGISTRY = {
    "DRAFT": DRAFT,
    "TWO_FACTOR_ENABLED": TWO_FACTOR_ENABLED,
    "TWO_FACTOR_DISABLED": TWO_FACTOR_DISABLED,
}
