from .models import db, \
    Property, \
    Issuer, \
    VcType
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
        properties = json_schema["properties"]
        for prop in properties:
            property = Property.query.filter(
                Property.name == properties[prop]["name"]
            ).first()
            if not property:
                new_property = Property(
                    name=properties[prop]["name"]
                )
                db.session.add(new_property)
            if extract_nested_properties:
                get_nested_properties(properties[prop])
        issuer_name = json_schema["issuer"]
        issuer = Issuer.query.filter(
            Issuer.name == issuer_name
        ).first()
        if not issuer:
            new_issuer = Issuer(
                name=issuer_name
            )
            db.session.add(new_issuer)
        vc_type_name = json_schema["credential_type"]
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
        db.session.commit()
        return _("Schema \"{type_name}\" uploaded").format(type_name=vc_type_name)
    else:
        return _("Schema not valid")


def get_nested_properties(json_data):
    print(json_data)
    if "properties" in json_data:
        properties = json_data["properties"]
        for prop in properties:
            property = Property.query.filter(
                Property.name == properties[prop]["name"]
            ).first()
            if not property:
                new_property = Property(
                    name=properties[prop]["name"]
                )
                db.session.add(new_property)
            get_nested_properties(prop)


def get_schema_by_json_data(json_schema, extract_nested_properties):
    if validate_json_schema(json_schema):
        properties = json_schema["properties"]
        for prop in properties:
            property = Property.query.filter(
                Property.name == properties[prop]["name"]
            ).first()
            if not property:
                new_property = Property(
                    name=properties[prop]["name"]
                )
                db.session.add(new_property)
            if extract_nested_properties:
                get_nested_properties(properties[prop])
        issuer_name = json_schema["issuer"]
        issuer = Issuer.query.filter(
            Issuer.name == issuer_name
        ).first()
        if not issuer:
            new_issuer = Issuer(
                name=issuer_name
            )
            db.session.add(new_issuer)
        vc_type_name = json_schema["credential_type"]
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
        db.session.commit()
        return _("Schema \"{type_name}\" uploaded").format(type_name=vc_type_name)
    else:
        return _("Schema not valid")


def validate_json_schema(schema):
    try:
        Draft7Validator.check_schema(schema)
    except SchemaError as schemaError:
        print(schemaError)
        return False
    return True
