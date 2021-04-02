from flask import current_app as app, make_response
from .models import db, \
    Property, \
    Issuer, \
    VcType, \
    Schema, \
    VcProfile, \
    association_table, \
    SdStatement
from sqlalchemy import or_
import json
import urllib
from flask_babel import _
from jsonschema import Draft7Validator, \
    SchemaError


def get_schema_by_url(url, extract_nested_properties):
    f = urllib.request.urlopen(url)
    content = f.read()
    json_schema = json.loads(content)
    if validate_json_schema(json_schema):
        schema_name = json_schema["$schema"]
        issuer_name = json_schema["issuer"]
        vc_type_name = json_schema["credential_type"]
        existing_schema = Schema.query.filter(
            Schema.name == schema_name
        ).first()
        if existing_schema:
            return _("Schema \"{schema_name}\" already exist").format(schema_name=schema_name)
        issuer = Issuer.query.filter(
            Issuer.name == issuer_name
        ).first()
        if not issuer:
            new_issuer = Issuer(
                name=issuer_name
            )
            issuer = new_issuer
            db.session.add(new_issuer)
        vc_type = VcType.query.filter(
            VcType.name == vc_type_name
        ).first()
        if not vc_type:
            new_vc_type = VcType(
                name=vc_type_name
            )
            db.session.add(new_vc_type)
        else:
            return _("Schema \"{type_name}\" already exist").format(type_name=vc_type_name)
        new_schema = Schema(
            name=schema_name,
            issuer=issuer,
            type=new_vc_type
        )
        db.session.add(new_schema)
        properties = json_schema["properties"]
        for prop in properties:
            new_property = Property(
                name=properties[prop]["name"],
                schema=new_schema
            )
            db.session.add(new_property)
            if extract_nested_properties:
                get_nested_properties(properties[prop], new_schema)
        db.session.commit()
        print(vc_type_name)
        return _("Schema \"{type_name}\" uploaded").format(type_name=vc_type_name)
    else:
        return _("Schema not valid")


def get_nested_properties(json_data, new_schema):
    if "properties" in json_data:
        properties = json_data["properties"]
        for prop in properties:
            new_property = Property(
                name=properties[prop]["name"],
                schema=new_schema
            )
            db.session.add(new_property)
            get_nested_properties(prop, new_schema)


def list_all_properties(json_data,prop_list):
    if "properties" in json_data:
        properties = json_data["properties"]
        for prop in properties:
            prop_list.append(properties[prop]["name"])
            list_all_properties(prop, prop_list)
    return prop_list


def get_schema_by_json_data(json_schema, extract_nested_properties):
    if validate_json_schema(json_schema):
        schema_name = json_schema["$schema"]
        issuer_name = json_schema["issuer"]
        vc_type_name = json_schema["credential_type"]
        existing_schema = Schema.query.filter(
            Schema.name == schema_name
        ).first()
        if existing_schema:
            return _("Schema \"{schema_name}\" already exist").format(schema_name=schema_name)
        issuer = Issuer.query.filter(
            Issuer.name == issuer_name
        ).first()
        if not issuer:
            new_issuer = Issuer(
                name=issuer_name
            )
            issuer = new_issuer
            db.session.add(new_issuer)
        vc_type = VcType.query.filter(
            VcType.name == vc_type_name
        ).first()
        if not vc_type:
            new_vc_type = VcType(
                name=vc_type_name
            )
            db.session.add(new_vc_type)
        else:
            return _("Schema \"{type_name}\" already exist").format(type_name=vc_type_name)
        new_schema = Schema(
            name=schema_name,
            issuer=issuer,
            type=new_vc_type
        )
        db.session.add(new_schema)
        properties = json_schema["properties"]
        for prop in properties:
            new_property = Property(
                name=properties[prop]["name"],
                schema=new_schema
            )
            db.session.add(new_property)
            if extract_nested_properties:
                get_nested_properties(properties[prop], new_schema)
        db.session.commit()
        print(vc_type_name)
        return _("Schema \"{type_name}\" uploaded").format(type_name=vc_type_name)
    else:
        return _("Schema not valid")


def replace_schema_by_json_data(json_schema, schema_id):
    if validate_json_schema(json_schema):
        issuer_name = json_schema["issuer"]
        vc_type_name = json_schema["credential_type"]
        existing_schema = Schema.query.filter(
            Schema.id == schema_id
        ).first()
        vc_type = VcType.query.filter(
            VcType.name == vc_type_name
        ).first()
        if not vc_type:
            return _("Can't replace schema: schema \"{type_name}\" doesn't exist").format(type_name=vc_type_name)

        new_properties = list_all_properties(json_schema, [])
        print("3", new_properties)
        old_properties = Property.query.filter(
            Property.schema_id == schema_id
        ).all()
        prop_to_remove = []
        prop_to_add = []
        for old_prop in old_properties:
            is_in_new = False
            for new_prop in new_properties:
                if old_prop.name == new_prop:
                    is_in_new = True
            if not is_in_new:
                prop_to_remove.append(old_prop)
        for new_prop in new_properties:
            is_in_old = False
            for old_prop in old_properties:
                if new_prop == old_prop.name:
                    is_in_old = True
            if not is_in_old:
                prop_to_add.append(new_prop)
        print("TO REMOVE", prop_to_remove)
        print("TO ADD", prop_to_add)
        if check_if_schema_is_used_with_properties(prop_to_remove):
            return _("Can't replace schema: Some properties you want to replace are used in profiles or statements")
        issuer = Issuer.query.filter(
            Issuer.name == issuer_name
        ).first()
        if existing_schema.issuer.name != issuer_name:
            print(existing_schema.issuer.name)
            old_issuer = Issuer.query.filter(
                Issuer.name == existing_schema.issuer.name
            ).first()
            existing_profile_with_issuer = VcProfile.query.filter(
                VcProfile.issuer_id == old_issuer.id
            ).first()
            if existing_profile_with_issuer:
                return _("Can't replace schema: The issuer in the old schema is used in some profiles")
            db.session.delete(old_issuer)
            if not issuer:
                new_issuer = Issuer(
                    name=issuer_name
                )
                db.session.add(new_issuer)
                existing_schema.issuer = new_issuer
        for prop in prop_to_remove:
            old_prop = Property.query.filter(
                Property.schema_id == schema_id,
                Property.name == prop.name
            ).first()
            db.session.delete(old_prop)
        for prop in prop_to_add:
            new_property = Property(
                name=prop,
                schema=existing_schema
            )
            db.session.add(new_property)
        db.session.commit()
        print(vc_type_name)
        return _("Schema \"{type_name}\" replaced").format(type_name=vc_type_name)
    else:
        return _("Schema not valid")


def delete_schema_by_schema_id(schema_id):
    existing_schema = Schema.query.filter(
        Schema.id == schema_id
    ).first()
    if existing_schema:
        print(existing_schema)
        print(existing_schema.issuer)
        print(existing_schema.issuer.id)
        db.session.delete(existing_schema.type)
        for prop in existing_schema.properties:
            db.session.delete(prop)
        issuer_id = existing_schema.issuer.id
        existing_other_schema_with_same_issuer = Schema.query.filter(
            Schema.issuer_id == issuer_id,
            Schema.name != existing_schema.name
        ).first()
        if not existing_other_schema_with_same_issuer:
            db.session.delete(existing_schema.issuer)
        db.session.delete(existing_schema)
        db.session.commit()
        return make_response(_("Schema with id {schema_id} deleted").format(schema_id=str(schema_id)))
    else:
        return make_response(_("Schema with id {schema_id} doesn't exist").format(schema_id=str(schema_id)))


def replace_schema_by_json_url(url, schema_id):
    f = urllib.request.urlopen(url)
    content = f.read()
    json_schema = json.loads(content)
    if validate_json_schema(json_schema):
        issuer_name = json_schema["issuer"]
        vc_type_name = json_schema["credential_type"]
        existing_schema = Schema.query.filter(
            Schema.id == schema_id
        ).first()
        vc_type = VcType.query.filter(
            VcType.name == vc_type_name
        ).first()
        if not vc_type:
            return _("Can't replace schema: schema \"{type_name}\" doesn't exist").format(type_name=vc_type_name)

        new_properties = list_all_properties(json_schema, [])
        print("3", new_properties)
        old_properties = Property.query.filter(
            Property.schema_id == schema_id
        ).all()
        prop_to_remove = []
        prop_to_add = []
        for old_prop in old_properties:
            is_in_new = False
            for new_prop in new_properties:
                if old_prop.name == new_prop:
                    is_in_new = True
            if not is_in_new:
                prop_to_remove.append(old_prop)
        for new_prop in new_properties:
            is_in_old = False
            for old_prop in old_properties:
                if new_prop == old_prop.name:
                    is_in_old = True
            if not is_in_old:
                prop_to_add.append(new_prop)
        print("TO REMOVE", prop_to_remove)
        print("TO ADD", prop_to_add)
        if check_if_schema_is_used_with_properties(prop_to_remove):
            return _("Can't replace schema: Some properties you want to replace are used in profiles or statements")
        issuer = Issuer.query.filter(
            Issuer.name == issuer_name
        ).first()
        if existing_schema.issuer.name != issuer_name:
            print(existing_schema.issuer.name)
            old_issuer = Issuer.query.filter(
                Issuer.name == existing_schema.issuer.name
            ).first()
            existing_profile_with_issuer = VcProfile.query.filter(
                VcProfile.issuer_id == old_issuer.id
            ).first()
            if existing_profile_with_issuer:
                return _("Can't replace schema: The issuer in the old schema is used in some profiles")
            db.session.delete(old_issuer)
            if not issuer:
                new_issuer = Issuer(
                    name=issuer_name
                )
                db.session.add(new_issuer)
                existing_schema.issuer = new_issuer
        for prop in prop_to_remove:
            old_prop = Property.query.filter(
                Property.schema_id == schema_id,
                Property.name == prop.name
            ).first()
            db.session.delete(old_prop)
        for prop in prop_to_add:
            new_property = Property(
                name=prop,
                schema=existing_schema
            )
            db.session.add(new_property)
        db.session.commit()
        print(vc_type_name)
        return _("Schema \"{type_name}\" replaced").format(type_name=vc_type_name)
    else:
        return _("Schema not valid")


def validate_json_schema(schema):
    try:
        Draft7Validator.check_schema(schema)
    except SchemaError as schemaError:
        print(schemaError)
        return False
    return True


def read_schema_by_id(schema_id):
    schema = Schema.query.filter(
        Schema.id == schema_id
    ).first()
    return schema


def check_if_schema_is_used(schema_id):
    existing_schema = Schema.query.filter(
        Schema.id == schema_id
    ).first()
    type_id = existing_schema.type_id
    issuer_id = existing_schema.issuer_id
    existing_profiles = VcProfile.query.filter(or_(
        VcProfile.type_id == type_id,
        VcProfile.issuer_id == issuer_id
    )).all()
    properties = Property.query.filter(
        Property.schema_id == schema_id
    ).all()
    for prop in properties:
        prop_in_statement = Property.query.join(association_table).join(SdStatement).filter(
            association_table.c.property_id == prop.id
        ).all()
        if len(prop_in_statement) > 0:
            return True
    if len(existing_profiles) > 0:
        return True
    return False


def check_if_schema_is_used_with_properties(properties):
    for prop in properties:
        prop_in_statement = Property.query.join(association_table).join(SdStatement).filter(
            association_table.c.property_id == prop.id
        ).all()
        if len(prop_in_statement) > 0:
            return True
    return False


def search_schema_by_arg(search_str):
    schemas = []
    existing_schemas = Schema.query.all()
    for schema in existing_schemas:
        if schema not in schemas and search_str.lower() in (schema.name.lower() or
                                  schema.issuer.name.lower() or
                                  schema.type.name.lower()):
            schemas.append(schema)
        else:
            for prop in schema.properties:
                if schema not in schemas and search_str.lower() in prop.name.lower():
                    schemas.append(schema)
    return schemas


test_schema = """{
    "$schema": "http://example.com/example3CreditCard",
    "issuer": "https://bigbigbank.com/issuer/UK",
    "credential_type": "ExampleCreditCard3",
    "type": "object",
    "properties": {
        "creditCardNumber": {
            "name": "credentialSubject.ex3credcard.number",
            "type": "string",
            "pattern": "^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}$",
            "example": "1111-2222-3333-4444"
        },
        "owner": {
            "name": "credentialSubject.ex3credcard.owner",
            "type": "string",
            "maxLength": 64
        },
        "expiringDate": {
            "name": "credentialSubject.ex3credcard.expiringDate",
            "format": "date"
        }
    },
    "required": [ "creditCardNumber", "owner", "expiringDate" ]
}"""


@app.route('/get_test_schema', methods=['GET'])
def get_test_schema():
    return test_schema
