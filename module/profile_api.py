from flask import request, make_response, render_template
from flask import current_app as app, abort, Response
from sqlalchemy import func
from .models import db, \
    VcProfile, \
    Issuer, \
    VcType
from flask_babel import _
import json


@app.route('/v1/vcprofile/create', methods=['GET'])
def create_vc_profile():
    """Create a vc_profile via query string parameters."""
    profile_name = request.args.get('profileName')
    profile_type = request.args.get('type')
    issuer_name = request.args.get('issuer')
    if profile_name and profile_type and issuer_name:
        existing_vc_profile = VcProfile.query.filter(
            VcProfile.name == profile_name
        ).first()
        if existing_vc_profile:
            return Response(status=409)
        issuer = Issuer.query.filter(
            Issuer.name == issuer_name
        ).first()
        vc_type = VcType.query.filter(
            VcType.name == profile_type
        ).first()
        if not issuer:
            return Response(status=400)
        if not vc_type:
            return Response(status=400)
        new_vc_profile = VcProfile(
            name=profile_name,
            type=vc_type,
            issuer=issuer
        )
        db.session.add(new_vc_profile)
        db.session.commit()
        return Response(status=201)
    else:
        return Response(status=400)


@app.route('/v1/vcprofile/read', methods=['GET'])
def read_vc_profile():
    """Read a vc_profile via query string parameters."""
    profile_name = request.args.get('profileName')
    if profile_name:
        existing_vc_profile = VcProfile.query.filter(
            func.lower(VcProfile.name) == func.lower(profile_name)
        ).first()
        if existing_vc_profile:
            res = json.dumps(existing_vc_profile.asdict(),
                             sort_keys=False,
                             indent=2)
            return res, 200
        else:
            abort(404)
    else:
        abort(404)


def read_vc_profile_by_id(profile_id):
    """Read a vc_profile via id."""
    existing_vc_profile = VcProfile.query.filter(
        VcProfile.id == profile_id
    ).first()
    if existing_vc_profile:
        return existing_vc_profile.asdict()
    else:
        return make_response(_("VC Profile with id {profile_id} doesn't exist").format(profile_id=profile_id))


@app.route('/v1/vcprofile/update', methods=['GET'])
def update_vc_profile():
    """Update a vc_profile via query string parameters."""
    profile_name = request.args.get('profileName')
    profile_type = request.args.get('type')
    issuer = request.args.get('issuer')
    if profile_name:
        existing_vc_profile = VcProfile.query.filter(
            VcProfile.name == profile_name
        ).first()
        if existing_vc_profile:
            if profile_type:
                existing_type = VcType.query.filter(
                    VcType.name == profile_type
                ).first()
                if existing_type:
                    existing_vc_profile.type = existing_type
                else:
                    return Response(status=400)

            if issuer:
                existing_issuer = Issuer.query.filter(
                    Issuer.name == issuer
                ).first()
                if existing_issuer:
                    existing_vc_profile.issuer = existing_issuer
                else:
                    return Response(status=400)
            db.session.commit()
            res = json.dumps(existing_vc_profile.asdict(),
                             sort_keys=False,
                             indent=2)
            return res, 200
        else:
            return Response(status=400)
    else:
        return Response(status=400)


def update_vc_profile_by_id(profile_name, profile_type, issuer, profile_id):
    """Update a vc_profile via id."""
    print("update_vc_profile_by_id", profile_name, profile_type, issuer, profile_id)
    existing_vc_profile = VcProfile.query.filter(
        VcProfile.id == profile_id
    ).first()
    existing_issuer = Issuer.query.filter(
        Issuer.name == issuer
    ).first()
    existing_type = VcType.query.filter(
        VcType.name == profile_type
    ).first()
    if existing_vc_profile and existing_issuer:
        existing_vc_profile.type = existing_type
        existing_vc_profile.issuer = existing_issuer
        existing_vc_profile.name = profile_name
        db.session.commit()
        return True
    else:
        return False


@app.route('/v1/vcprofile/search', methods=['GET'])
def search_vc_profile():
    """Search a vc_profile via query string parameters."""
    profiles = []
    profile_name = request.args.get('profileName')
    profile_type = request.args.get('type')

    if profile_name and profile_type:
        existing_vc_profiles = VcProfile.query.filter(
            func.lower(VcProfile.name.contains(func.lower(profile_name))),
            func.lower(VcProfile.type.contains(func.lower(profile_type)))
        ).all()
        for profile in existing_vc_profiles:
            profiles.append(profile.asdict())
    elif profile_name:
        existing_vc_profiles = VcProfile.query.filter(
            func.lower(VcProfile.name.contains(func.lower(profile_name)))
        ).all()
        for profile in existing_vc_profiles:
            profiles.append(profile.asdict())
    elif profile_type:
        existing_types = VcType.query.filter(
            func.lower(VcType.name.contains(func.lower(profile_type)))
        ).all()
        for existing_type in existing_types:
            existing_vc_profiles = VcProfile.query.filter(
                VcProfile.type_id == existing_type.id
            ).all()
            for profile in existing_vc_profiles:
                profiles.append(profile.asdict())
    else:
        return Response(status=400)
    if len(profiles) == 0:
        return Response(status=204)
    res = json.dumps(profiles,
                     sort_keys=False,
                     indent=2)
    return res, 200


def search_vc_profile_by_arg(search_str):
    """Search a vc_profile via arguments"""
    profiles = []
    existing_vc_profiles = db.session.query(VcProfile).join(Issuer).join(VcType).filter(
        func.lower(Issuer.name.contains(func.lower(search_str))) |
        func.lower(VcType.name.contains(func.lower(search_str)))
    ).all()
    for profile in existing_vc_profiles:
        profiles.append(profile)
    return profiles


@app.route('/v1/vcprofile/delete', methods=['GET'])
def delete_vc_profile():
    """Delete a vc_profile via query string parameters."""
    profile_name = request.args.get('profileName')
    if profile_name:
        existing_vc_profile = VcProfile.query.filter(
            VcProfile.name == profile_name
        ).first()
        if existing_vc_profile:
            db.session.delete(existing_vc_profile)
            db.session.commit()
            return Response(status=200)
        else:
            return Response(status=400)
    else:
        return Response(status=400)


def delete_vc_profile_by_id(profile_id):
    """Delete a vc_profile via its id."""
    existing_vc_profile = VcProfile.query.filter(
        VcProfile.id == profile_id
    ).first()
    if existing_vc_profile:
        db.session.delete(existing_vc_profile)
        db.session.commit()
        return make_response(_("VC Profile with id {profile_id} deleted").format(profile_id=str(profile_id)))
    else:
        return make_response(_("VC Profile with id {profile_id} doesn't exist").format(profile_id=str(profile_id)))


def get_vc_profile_id(profile_name):
    """Get a vc_profile id from the profile name."""
    vc_profile = VcProfile.query.filter(
        VcProfile.name == profile_name
    ).first()
    if vc_profile:
        return vc_profile.id
    else:
        return -1


def get_vc_profile(profile_name):
    """Get a vc_profile from the profile name."""
    vc_profile = VcProfile.query.filter(
        VcProfile.name == profile_name
    ).first()
    if vc_profile:
        return vc_profile
    else:
        return None
