# Email Sending Abstraction

This project provides an abstraction layer for sending emails via different email service providers.  
All email sending is performed through a unified **service layer** (`EmailService`) which delegates to the configured provider:

```python
# Short example using the service layer:
await email_service.send(
    to="recipient@example.com",
    subject="Test email",
    body="Hello, this is a test email.",
    html="<p>Hello, this is a test email.</p>"
)
```

The specific email provider is selected via an environment variable.

---

## Selecting an Email Provider

The email provider is configured in the `.env` file:

```env
EMAIL_SERVICE='mailtrap'   # 'mailtrap', 'mailjet', or 'dummy'
```

Available options:

- `'mailtrap'`
- `'mailjet'`
- `'dummy'` – stores emails locally in a file for testing, does **not** send real emails

Switching the value of `EMAIL_SERVICE` changes the active provider without modifying application logic.

---

## Adding a New Email Provider

To add a new email provider:

1. Create a new provider implementation file inside the `providers/` directory.
2. Register the provider in `registry.py` by adding it to the provider registry.

Example:

```python
EMAIL_PROVIDERS = {
    "mailtrap": MailtrapEmailService,
    "mailjet": MailjetEmailService,
    "dummy": DummyEmailService,
    "newprovider": NewEmailService
}
```

After registration, the newly added provider can be selected via the `.env` configuration:

```env
EMAIL_SERVICE='newprovider'
```

Once configured, the application will automatically use the new provider through the `EmailService.send(...)` abstraction.

---

## Provider-Specific Behavior

### Dummy Provider

When using:

```env
EMAIL_SERVICE='dummy'
```

- Emails are **written to a local file** (usually `emails.log`) instead of being sent.  
- Ideal for **development and automated tests**, when no real email delivery is needed.  
- This prevents `ConfigurationException` errors related to missing real email credentials.

---

### Mailtrap

When using:

```env
EMAIL_SERVICE='mailtrap'
```

- Emails can be viewed in your Mailtrap inbox:  
  [https://mailtrap.io/inboxes](https://mailtrap.io/inboxes)  
- You must be logged in with a registered Mailtrap account.  
- The recipient email address can be **any value**.  
- Emails are **not delivered** to real recipients.  
- Messages are captured and displayed only inside the Mailtrap sandbox.

This option is ideal for development and testing.  
Official documentation: [Mailtrap Docs](https://mailtrap.io/docs)  
Register a free account: [Mailtrap Sign Up](https://mailtrap.io/signup)

---

### Mailjet

When using:

```env
EMAIL_SERVICE='mailjet'
```

- The recipient email address **must be a real, existing address**.  
- Emails are actually delivered to the specified recipient.  
- When using a public email service (Gmail, Yahoo, Hotmail, etc.), messages may appear in **Spam**.  
- This is a common limitation of the free version of Mailjet.

This option is suitable for real email delivery scenarios.  
Official documentation: [Mailjet Docs](https://www.mailjet.com/docs/)  
Register a free account: [Mailjet Sign Up](https://app.mailjet.com/signup)

---

## Summary

- Use `EmailService.send(...)` throughout the application.  
- Switch providers via the `.env` configuration.  
- Extend functionality by adding new provider implementations and registering them in `registry.py`.  
- For testing, the **dummy provider** avoids sending real emails while preserving full integration.

This approach keeps the email-sending logic clean, flexible, and easily extensible.