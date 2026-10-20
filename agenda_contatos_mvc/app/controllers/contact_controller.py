from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.services.contact_service import ValidationError


def create_contact_blueprint():
    contacts = Blueprint("contacts", __name__)

    def service():
        return current_app.extensions["contact_service"]

    @contacts.route("/")
    def index():
        group = request.args.get("grupo", "").strip() or None
        contact_list = service().list_contacts(group)
        return render_template(
            "index.html",
            contatos=contact_list,
            grupo=group,
        )

    @contacts.route("/cadastrar", methods=["GET", "POST"])
    def cadastrar():
        if request.method == "POST":
            try:
                service().create_contact(
                    request.form.get("nome"),
                    request.form.get("telefone"),
                    request.form.get("email"),
                    request.form.get("grupo"),
                )
                flash("Contato cadastrado com sucesso!", "sucesso")
                return redirect(url_for("contacts.index"))
            except ValidationError as error:
                flash(str(error), "erro")

        return render_template("cadastrar.html")

    @contacts.route("/buscar", methods=["GET", "POST"])
    def buscar():
        resultados = []
        pesquisado = False
        termo = ""

        if request.method == "POST":
            termo = request.form.get("nome", "").strip()
            pesquisado = True
            try:
                resultados = service().search_contacts(termo)
            except ValidationError as error:
                flash(str(error), "erro")

        return render_template(
            "buscar.html",
            contatos=resultados,
            pesquisado=pesquisado,
            termo=termo,
        )

    @contacts.route("/editar/<int:contact_id>", methods=["GET", "POST"])
    def editar(contact_id):
        contact = service().get_contact(contact_id)

        if contact is None:
            flash("Contato não encontrado.", "erro")
            return redirect(url_for("contacts.index"))

        if request.method == "POST":
            try:
                updated = service().update_contact(
                    contact_id,
                    request.form.get("nome"),
                    request.form.get("telefone"),
                    request.form.get("email"),
                    request.form.get("grupo"),
                )
                if not updated:
                    flash("Não foi possível atualizar o contato.", "erro")
                    return redirect(url_for("contacts.index"))

                flash("Contato atualizado com sucesso!", "sucesso")
                return redirect(url_for("contacts.index"))
            except ValidationError as error:
                flash(str(error), "erro")

        return render_template("editar.html", contato=contact)

    @contacts.route("/remover/<int:contact_id>", methods=["POST"])
    def remover(contact_id):
        if service().delete_contact(contact_id):
            flash("Contato removido com sucesso.", "sucesso")
        else:
            flash("Contato não encontrado.", "erro")
        return redirect(url_for("contacts.index"))

    return contacts
