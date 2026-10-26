# app/contacts/types.py

from enum import StrEnum


class ContactType(StrEnum):
    EMAIL = "email"
    PHONE = "phone"
