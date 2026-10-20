import re
from app.models.contact import Contact


class ValidationError(ValueError):
    ""


class ContactService:

    GROUPS = (
        "Família",
        "Amigos",
        "Trabalho",
        "Estudos",
        "Outros",
    )

    def __init__(self, repository):
        self.repository = repository

    @staticmethod
    def _clean_and_validate(name, phone, email, group):
        values = {
            "name": (name or "").strip(),
            "phone": (phone or "").strip(),
            "email": (email or "").strip(),
            "group": (group or "").strip(),
        }

        if not all(values.values()):
            raise ValidationError("Preencha todos os campos.")

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            values["email"],
        ):
            raise ValidationError("Informe um e-mail válido.")

        if not any(char.isdigit() for char in values["phone"]):
            raise ValidationError("Informe um telefone válido.")

        return values

    def _validate_unique(self, phone, email, exclude_id=None):
        message = self.repository.find_duplicate(
            phone,
            email,
            exclude_id=exclude_id,
        )

        if message:
            raise ValidationError(message)

    def list_contacts(self, group=None):
        if group:
            return self.repository.list_by_group(group)
        return self.repository.list_all()

    def search_contacts(self, name):
        name = (name or "").strip()

        if not name:
            raise ValidationError(
                "Digite um nome para pesquisar."
            )

        return self.repository.search_by_name(name)

    def get_contact(self, contact_id):
        return self.repository.get_by_id(contact_id)

    def create_contact(self, name, phone, email, group):
        values = self._clean_and_validate(
            name, phone, email, group
        )

        self._validate_unique(
            values["phone"],
            values["email"],
        )

        contact = Contact(id=None, **values)
        return self.repository.create(contact)

    def update_contact(
        self, contact_id, name, phone, email, group
    ):
        values = self._clean_and_validate(
            name, phone, email, group
        )

        self._validate_unique(
            values["phone"],
            values["email"],
            exclude_id=contact_id,
        )

        contact = Contact(id=contact_id, **values)
        return self.repository.update(contact)

    def delete_contact(self, contact_id):
        return self.repository.delete(contact_id)
