import sqlite3

from app.models.contact import Contact


class ContactRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _to_contact(row):
        if row is None:
            return None
        return Contact(
            id=row["id"],
            name=row["nome"],
            phone=row["telefone"],
            email=row["email"],
            group=row["grupo"],
        )

    def initialize_database(self):
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS contatos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    grupo TEXT NOT NULL
                )
            """)

    def list_all(self):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM contatos ORDER BY nome"
            ).fetchall()
        return [self._to_contact(row) for row in rows]

    def list_by_group(self, group):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM contatos WHERE grupo = ? ORDER BY nome",
                (group,),
            ).fetchall()
        return [self._to_contact(row) for row in rows]

    def search_by_name(self, name):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM contatos WHERE nome LIKE ? ORDER BY nome",
                (f"%{name}%",),
            ).fetchall()
        return [self._to_contact(row) for row in rows]

    def get_by_id(self, contact_id):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM contatos WHERE id = ?",
                (contact_id,),
            ).fetchone()
        return self._to_contact(row)


    def find_duplicate(self, phone, email, exclude_id=None):
        phone_digits = "".join(filter(str.isdigit, phone))
        email_normalized = email.strip().casefold()

        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, telefone, email FROM contatos"
            ).fetchall()

        for row in rows:
            if exclude_id is not None and row["id"] == exclude_id:
                continue

            existing_phone = "".join(
                filter(str.isdigit, row["telefone"])
            )
            existing_email = row["email"].strip().casefold()

            if phone_digits == existing_phone:
                return "Este telefone já está cadastrado."

            if email_normalized == existing_email:
                return "Este e-mail já está cadastrado."

        return None

    def create(self, contact):
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO contatos (nome, telefone, email, grupo)
                VALUES (?, ?, ?, ?)
                """,
                (contact.name, contact.phone, contact.email, contact.group),
            )
            new_id = cursor.lastrowid
        return self.get_by_id(new_id)

    def update(self, contact):
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE contatos
                SET nome = ?, telefone = ?, email = ?, grupo = ?
                WHERE id = ?
                """,
                (
                    contact.name,
                    contact.phone,
                    contact.email,
                    contact.group,
                    contact.id,
                ),
            )
        return cursor.rowcount > 0

    def delete(self, contact_id):
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM contatos WHERE id = ?",
                (contact_id,),
            )
        return cursor.rowcount > 0
