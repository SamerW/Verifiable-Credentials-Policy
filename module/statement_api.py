from flask import request, make_response
from flask import current_app as app
from .models import db, \
    SdStatement, \
    Property, \
    association_table
from flask_babel import _


@app.route('/create_sd_statement', methods=['GET'])
def create_sd_statement():
    """Create a sd_statement via query string parameters."""
    sd_name = request.args.get('sdName')
    requires = request.args.getlist('requires')
    if sd_name and requires:
        existing_sd_statement = SdStatement.query.filter(
            SdStatement.name == sd_name
        ).first()
        if existing_sd_statement:
            return make_response(_("Sd Statement with name {sd_name} already exists").format(sd_name=sd_name))
        existing_sd_statement = SdStatement(name=sd_name)
        for r in requires:
            existing_sd_statement.properties.append(Property(name=r))
        db.session.add(existing_sd_statement)
        db.session.commit()
        return make_response(_("Sd Statement Created"))
    else:
        return make_response(_("Required argument(s) missing"))


@app.route('/read_sd_statement', methods=['GET'])
def read_sd_statement():
    """Read a sd_statement via query string parameters."""
    sd_name = request.args.get('sdName')
    if sd_name:
        existing_sd_statement = SdStatement.query.filter(
            SdStatement.name == sd_name
        ).first()
        if existing_sd_statement:
            return make_response(existing_sd_statement.asdict())
        else:
            return make_response(_("Sd Statement with name {sd_name} doesn't exist").format(sd_name=sd_name))
    else:
        return make_response(_("Required argument(s) missing"))


def read_sd_statement_by_id(statement_id):
    """Read a sd_statement via id."""
    existing_sd_statement = SdStatement.query.filter(
        SdStatement.id == statement_id
    ).first()
    if existing_sd_statement:
        return existing_sd_statement.asdict()
    else:
        return make_response(_("Sd Statement with id {statement_id} doesn't exist").format(statement_id=str(statement_id)))


@app.route('/update_sd_statement', methods=['GET'])
def update_sd_statement():
    """Update a sd_statement via query string parameters."""
    sd_name = request.args.get('sdName')
    requires = request.args.getlist('requires')
    if sd_name:
        existing_sd_statement = SdStatement.query.filter(
            SdStatement.name == sd_name
        ).first()
        if existing_sd_statement:
            existing_sd_statement.properties = []
            for r in requires:
                existing_sd_statement.properties.append(Property(name=r))
                db.session.commit()
            return make_response(existing_sd_statement.asdict())
        else:
            existing_sd_statement = SdStatement(name=sd_name)
            for r in requires:
                existing_sd_statement.properties.append(Property(name=r))
            db.session.add(existing_sd_statement)
            db.session.commit()
            return make_response(existing_sd_statement.asdict())
    else:
        return make_response(_("Required argument(s) missing"))


def update_sd_statement_by_id(statement_name, requires, statement_id):
    """Update a sd_statement via id."""
    existing_sd_statement = SdStatement.query.filter(
        SdStatement.id == statement_id
    ).first()
    print(existing_sd_statement)
    if existing_sd_statement:
        existing_sd_statement.name = statement_name
        existing_sd_statement.properties = []
        for r in requires:
            existing_property = Property.query.filter(
                Property.name == r
            ).first()
            existing_sd_statement.properties.append(existing_property)
        db.session.commit()
        return True
    else:
        return False


@app.route('/delete_sd_statement', methods=['GET'])
def delete_sd_statement():
    """Delete a sd_statement via query string parameters."""
    sd_name = request.args.get('sdName')
    if sd_name:
        existing_sd_statement = SdStatement.query.filter(
            SdStatement.name == sd_name
        ).first()
        if existing_sd_statement:
            db.session.delete(existing_sd_statement)
            db.session.commit()
            return make_response(_("Sd Statement name {sd_name} deleted").format(sd_name=sd_name))
        else:
            return make_response(_("Sd Statement name {sd_name} doesn't exist").format(sd_name=sd_name))
    else:
        return make_response(_("Required argument(s) missing"))


def delete_sd_statement_by_id(statement_id):
    """Delete a sd_statement via id."""
    existing_sd_statement = SdStatement.query.filter(
        SdStatement.id == statement_id
    ).first()
    if existing_sd_statement:
        db.session.delete(existing_sd_statement)
        db.session.commit()
        return make_response(_("Sd Statement with id {statement_id} deleted").format(statement_id=str(statement_id)))
    else:
        return make_response(_("Sd Statement with id {statement_id} doesn't exist").format(statement_id=str(statement_id)))


@app.route('/search_sd_statement', methods=['GET'])
def search_sd_statement_by_arg(search_str):
    """Search a sd_statement via arguments"""
    statements = []
    all_statements = SdStatement.query.all()
    for statement in all_statements:
        to_append = False
        statement_str = get_all_sd_statement_str(statement)
        for item in statement_str:
            lower_search_str = search_str.lower()
            lower_item = item.lower()
            if lower_search_str in lower_item:
                to_append = True
        if to_append:
            statements.append(statement)
    return statements


def get_sd_statement_id(sd_name):
    """Get a sd_statement id from the profile name."""
    sd_statement = SdStatement.query.filter(
        SdStatement.name == sd_name
    ).first()
    if sd_statement:
        return sd_statement.id
    else:
        return -1


def get_sd_statement(sd_name):
    """Get a sd_statement from the profile name."""
    sd_statement = SdStatement.query.filter(
        SdStatement.name == sd_name
    ).first()
    if sd_statement:
        return sd_statement
    else:
        return None


def get_all_sd_statement_str(sd_statement):
    statement_str = []
    statement_str.append(sd_statement.name)
    properties = Property.query.join(association_table).join(SdStatement).filter(
        association_table.c.sd_statement_id == sd_statement.id
    ).all()
    for prop in properties:
        statement_str.append(prop.name)
    return statement_str
