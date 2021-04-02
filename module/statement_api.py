from flask import request, make_response, render_template
from flask import current_app as app, Response
from sqlalchemy import exc, func
from .models import db, \
    SdStatement, \
    Property, \
    association_table
from flask_babel import _
import json


@app.route('/v1/sdstatement/create', methods=['GET'])
def create_sd_statement():
    """Create a sd_statement via query string parameters."""
    sd_name = request.args.get('sdName')
    requires = request.args.getlist('requires')
    if sd_name and requires != []:
        properties = Property.query.all()
        statement_properties = []
        properties_not_in_db = []
        for prop in requires:
            is_in_database = False
            for p in properties:
                if p.name == prop:
                    statement_properties.append(p)
                    is_in_database = True
            if not is_in_database:
                properties_not_in_db.append(prop)
        if properties_not_in_db != []:
            return Response(status=400)
        new_statement = SdStatement(
            name=sd_name,
            properties=statement_properties
        )
        db.session.add(new_statement)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as error:
            if error.__str__().__contains__("UNIQUE constraint failed"):
                db.session.rollback()
                return Response(status=409)
            else:
                return Response(status=500)
        res = json.dumps(new_statement.asdict(),
                         sort_keys=False,
                         indent=2)
        return res, 201
    else:
        return Response(status=400)


@app.route('/v1/sdstatement/read', methods=['GET'])
def read_sd_statement():
    """Read a sd_statement via query string parameters."""
    sd_name = request.args.get('sdName')
    if sd_name:
        existing_sd_statement = SdStatement.query.filter(
            SdStatement.name == sd_name
        ).first()
        if existing_sd_statement:
            res = json.dumps(existing_sd_statement.asdict(),
                             sort_keys=False,
                             indent=2)
            return res, 200
        else:
            return Response(status=404)
    else:
        return Response(status=404)


def read_sd_statement_by_id(statement_id):
    """Read a sd_statement via id."""
    existing_sd_statement = SdStatement.query.filter(
        SdStatement.id == statement_id
    ).first()
    if existing_sd_statement:
        return existing_sd_statement.asdict()
    else:
        return make_response(_("Sd Statement with id {statement_id} doesn't exist").format(statement_id=str(statement_id)))


@app.route('/v1/sdstatement/update', methods=['GET'])
def update_sd_statement():
    """Update a sd_statement via query string parameters."""
    sd_name = request.args.get('sdName')
    requires = request.args.getlist('requires')
    if sd_name:
        existing_sd_statement = SdStatement.query.filter(
            SdStatement.name == sd_name
        ).first()
        if existing_sd_statement:
            properties_not_in_db = []
            for prop in requires:
                is_in_database = False
                for p in existing_sd_statement.properties:
                    if p.name == prop:
                        is_in_database = True
                if not is_in_database:
                    properties_not_in_db.append(prop)
            if properties_not_in_db != []:
                return Response(status=400)
            if update_sd_statement_by_id(existing_sd_statement.name, requires, existing_sd_statement.id):
                return Response(status=200)
        else:
            return Response(status=400)
    else:
        return Response(status=400)


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
            if r == "All":
                pass
            else:
                existing_property = Property.query.filter(
                    Property.name == r
                ).first()
                existing_sd_statement.properties.append(existing_property)
        db.session.commit()
        return True
    else:
        return False


@app.route('/v1/sdstatement/delete', methods=['GET'])
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
            return Response(status=200)
        else:
            return Response(status=400)
    else:
        return Response(status=400)


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


@app.route('/v1/sdstatement/search', methods=['GET'])
def search_sd_statement():
    """Search a sd_statement via query string parameters."""
    statements = []
    sd_name = request.args.get('sd_name')
    require_str = request.args.get('requires')
    if sd_name and require_str:
        all_statements = SdStatement.query.all()
        for statement in all_statements:
            if  statement.name == sd_name:
                properties = Property.query.join(association_table).join(SdStatement).filter(
                    association_table.c.sd_statement_id == statement.id
                ).all()
                for prop in properties:
                    if require_str in prop.name:
                        statements.append(statement.asdict())
    elif sd_name:
        existing_statements = SdStatement.query.filter(
            SdStatement.name == sd_name
        ).all()
        for statement in existing_statements:
            statements.append(statement.asdict())
    elif require_str:
        all_statements = SdStatement.query.all()
        for statement in all_statements:
            properties = Property.query.join(association_table).join(SdStatement).filter(
                association_table.c.sd_statement_id == statement.id
            ).all()
            for prop in properties:
                if require_str in prop.name:
                    statements.append(statement.asdict())
    else:
        return Response(status=400)
    if len(statements) == 0:
        return Response(status=204)
    res = json.dumps(statements,
                     sort_keys=False,
                     indent=2)
    return res, 200


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
    """Get a sd_statement id from the sd name."""
    sd_statement = SdStatement.query.filter(
        SdStatement.name == sd_name
    ).first()
    if sd_statement:
        return sd_statement.id
    else:
        return -1


def get_sd_statement(sd_name):
    """Get a sd_statement from the sd name."""
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
