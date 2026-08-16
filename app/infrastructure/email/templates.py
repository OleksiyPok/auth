# app/infrastructure/email/templates.py

from string import Template

DRAFT = Template("""Subject: Request Submitted - $request_code - $request_title

Dear $user_name,
....

Best regards,
System
""")

TEMPLATE_REGISTRY = {
    "DRAFT": DRAFT,
}
