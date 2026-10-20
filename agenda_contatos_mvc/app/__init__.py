from pathlib import Path
from flask import Flask

from app.controllers.contact_controller import create_contact_blueprint
from app.repositories.contact_repository import ContactRepository
from app.services.contact_service import ContactService


def create_app():
    pasta_projeto = Path(__file__).resolve().parent.parent

    app = Flask(
        __name__,
        template_folder=str(pasta_projeto / "templates"),
        static_folder=str(pasta_projeto / "static")
    )

    app.config["SECRET_KEY"] = "agenda-contatos-chave"
    app.config["DATABASE"] = str(pasta_projeto / "agenda.db")

    repository = ContactRepository(app.config["DATABASE"])
    repository.initialize_database()

    service = ContactService(repository)
    app.extensions["contact_service"] = service

    app.register_blueprint(create_contact_blueprint())

    return app
