from flask import request, make_response
from flask import current_app as app
from sqlalchemy import func
from .models import db, \
    VcProfile, \
    Issuer, \
    VcType
from flask_babel import _
import json


@app.route('/create_vc_profile', methods=['GET'])
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
            return make_response(_("VC Profile with name {profile_name} already exists").format(profile_name=profile_name))
        issuer = Issuer.query.filter(
            Issuer.name == issuer_name
        ).first()
        vc_type = VcType.query.filter(
            VcType.name == profile_type
        ).first()
        if not issuer:
            return make_response(_("Issuer is not recognized"))
        if not vc_type:
            return make_response(_("Vc Type is not recognized"))
        new_vc_profile = VcProfile(
            name=profile_name,
            type=vc_type,
            issuer=issuer
        )
        db.session.add(new_vc_profile)
        db.session.commit()
        return make_response(_("VC Profile Created"))
    else:
        return make_response(_("Required argument(s) missing"))


@app.route('/read_vc_profile', methods=['GET'])
def read_vc_profile():
    """Read a vc_profile via query string parameters."""
    profile_name = request.args.get('profileName')
    if profile_name:
        existing_vc_profile = VcProfile.query.filter(
            VcProfile.name == profile_name
        ).first()
        if existing_vc_profile:
            return make_response(existing_vc_profile.asdict())
        else:
            return make_response(_("VC Profile with name {profile_name} doesn't exist").format(profile_name=profile_name))
    else:
        return make_response(_("Required argument missing"))


def read_vc_profile_by_id(profile_id):
    """Read a vc_profile via id."""
    existing_vc_profile = VcProfile.query.filter(
        VcProfile.id == profile_id
    ).first()
    if existing_vc_profile:
        return existing_vc_profile.asdict()
    else:
        return make_response(_("VC Profile with id {profile_id} doesn't exist").format(profile_id=profile_id))


@app.route('/update_vc_profile', methods=['GET'])
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
                existing_vc_profile.type = profile_type
            if issuer:
                existing_vc_profile.issuer = issuer
            db.session.commit()
            return make_response(existing_vc_profile.asdict())
        else:
            return make_response(_("VC Profile with name {profile_name} doesn't exist").format(profile_name=profile_name))
    else:
        return make_response(_("Required argument missing"))


def update_vc_profile_by_id(profile_name, profile_type, issuer, profile_id):
    """Update a vc_profile via id."""
    existing_vc_profile = VcProfile.query.filter(
        VcProfile.id == profile_id
    ).first()
    if existing_vc_profile:
        existing_vc_profile.type.name = profile_type
        existing_vc_profile.issuer.name = issuer
        existing_vc_profile.name = profile_name
        db.session.commit()
        return True
    else:
        return False


@app.route('/search_vc_profile', methods=['GET'])
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
        existing_vc_profiles = VcProfile.query.filter(
            func.lower(VcProfile.type.contains(func.lower(profile_type)))
        ).all()
        for profile in existing_vc_profiles:
            profiles.append(profile.asdict())
    else:
        return make_response(_("Required argument missing"))
    return json.dumps(profiles, indent=4)


@app.route('/search_vc_profile', methods=['GET'])
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


@app.route('/delete_vc_profile', methods=['GET'])
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
            return True
        else:
            return False
    else:
        return make_response(_("Required argument missing"))


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
