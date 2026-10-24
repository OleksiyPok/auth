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

MERGE_COMPLETED = Template("""Subject: Accounts merged

Another account was merged into your account. Its sign-in methods now belong to
this account, and the other account has been deactivated.

If you did not perform this action, please secure your account immediately.
""")

TEMPLATE_REGISTRY = {
    "DRAFT": DRAFT,
    "TWO_FACTOR_ENABLED": TWO_FACTOR_ENABLED,
    "TWO_FACTOR_DISABLED": TWO_FACTOR_DISABLED,
    "MERGE_COMPLETED": MERGE_COMPLETED,
}


def render_template(name: str, **values: str) -> tuple[str, str]:
    """Return the subject and the body of the template."""
    rendered = TEMPLATE_REGISTRY[name].substitute(**values).strip()
    subject, body = rendered.split("\n\n", 1)
    return subject.removeprefix("Subject: "), body
