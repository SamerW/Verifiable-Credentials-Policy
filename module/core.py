from flask import Blueprint, \
    render_template, \
    request, \
    redirect, \
    url_for
from flask_babel import _
from sqlalchemy import exc
from .models import db, \
    VcProfile, \
    Issuer, \
    VcType, \
    Property, \
    SdStatement, \
    Policies
from .profile_api import read_vc_profile_by_id, \
    search_vc_profile_by_arg, \
    delete_vc_profile_by_id, \
    update_vc_profile_by_id
from .statement_api import read_sd_statement_by_id, \
    search_sd_statement_by_arg, \
    delete_sd_statement_by_id, \
    update_sd_statement_by_id
from .policy_api import create_dnf_policy_from_json, \
    create_cnf_policy_from_json, \
    read_policy_by_policy_match_id, \
    search_policies_by_arg, \
    delete_policy_by_policy_match_id, \
    update_policy_by_id
from .schema_api import get_schema_by_json_data, get_schema_by_url
from .forms import ListPolicyForm, \
    ListPropertySelectionForm, \
    ListProfileForm
import json

bp = Blueprint('core', __name__)


@bp.route('/')
def index():
    return redirect(url_for("core.create_credential_profile"))


@bp.route('/credential_profile/create', methods=['GET', 'POST'])
def create_credential_profile():
    issuers_options = []
    vc_types_options = []
    issuers = Issuer.query.all()
    for issuer in issuers:
        issuers_options.append(issuer.name)
    vc_types = VcType.query.all()
    for vc_type in vc_types:
        vc_types_options.append(vc_type.name)
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        profile_name = None
        profile_issuer_name = None
        profile_vc_type_name = None
        if "crendential_profile_name" in form_dict:
            profile_name = form_dict["crendential_profile_name"]
        if "input_issuer" in form_dict:
            profile_issuer_name = form_dict["input_issuer"]
        if "input_vc_type" in form_dict:
            profile_vc_type_name = form_dict["input_vc_type"]
        if profile_name and profile_issuer_name and profile_vc_type_name:
            issuer = Issuer.query.filter(
                Issuer.name == profile_issuer_name
            ).first()
            vc_type = VcType.query.filter(
                VcType.name == profile_vc_type_name
            ).first()
            new_vc_profile = VcProfile(
                name=profile_name,
                issuer=issuer,
                type=vc_type
            )
            db.session.add(new_vc_profile)
            try:
                db.session.commit()
            except exc.SQLAlchemyError as error:
                if error.__str__().__contains__("UNIQUE constraint failed"):
                    message = _("Profile with name {profile_name} already exists.").format(profile_name=profile_name)
                else:
                    message = _("Unknown Error")
                return render_template(
                    '/credential_profile/create.html',
                    issuers_options=issuers_options,
                    vc_types_options=vc_types_options,
                    message=message)
            message = _("Profile created")
            return render_template(
                '/credential_profile/create.html',
                issuers_options=issuers_options,
                vc_types_options=vc_types_options,
                message=message)
        else:
            message = _("Please fill all parameters")
            return render_template(
                '/credential_profile/create.html',
                issuers_options=issuers_options,
                vc_types_options=vc_types_options,
                message=message)
    else:
        return render_template(
            '/credential_profile/create.html',
            issuers_options=issuers_options,
            vc_types_options=vc_types_options)


@bp.route('/credential_profile/update', methods=['GET', 'POST'])
def update_credential_profile():
    form_dict = request.form.to_dict()
    for key in form_dict.keys():
        if "modify" in key:
            prof_id = int(key.replace("modify_", ""))
            profile = read_vc_profile_by_id(prof_id)
            profile_name = profile["profileName"]
            issuers_options = []
            vc_types_options = []
            issuers = Issuer.query.all()
            for issuer in issuers:
                issuers_options.append(issuer.name)
            vc_types = VcType.query.all()
            for vc_type in vc_types:
                vc_types_options.append(vc_type.name)
            return render_template(
                '/credential_profile/update.html',
                profile_name=profile_name,
                issuers_options=issuers_options,
                vc_types_options=vc_types_options,
                prof_id=prof_id)
    if request.method == 'POST':
        for key in form_dict:
            if "prof_id" in key:
                prof_id = int(key.replace("prof_id_", ""))
                profile_name = form_dict["crendential_profile_name"]
                issuer = form_dict["input_issuer"]
                profile_type = form_dict["input_vc_type"]
                message = _("Could not update profile")
                if update_vc_profile_by_id(profile_name, profile_type, issuer, prof_id):
                    message = _("Profile updated")
                form = ListProfileForm()
                return render_template(
                    '/credential_profile/manage.html',
                    form=form,
                    message=message)


@bp.route('/credential_profile/manage', methods=['GET', 'POST'])
def manage_credential_profile():
    form = ListProfileForm()
    if request.method == 'GET':
        return render_template(
            '/credential_profile/manage.html',
            form=form)
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        if "profile" in form_dict:
            if form_dict["profile"] is not '':
                profiles = []
                profile_dict = {}
                profile = read_vc_profile_by_id(form_dict["profile"])
                profile_dict["str"] = render_profile(profile)
                profile_dict["id"] = form_dict["profile"]
                profiles.append(profile_dict)
                return render_template(
                    '/credential_profile/manage.html',
                    form=form,
                    profiles=profiles)
            else:
                return render_template(
                    '/credential_profile/manage.html',
                    form=form)
        elif "input_search_profile" in form_dict:
            input_str = form_dict["input_search_profile"]
            profiles = []
            profs = search_vc_profile_by_arg(input_str)
            for profile in profs:
                profile_dict = dict()
                profile_dict["str"] = render_profile(profile.asdict())
                profile_dict["id"] = profile.id
                profiles.append(profile_dict)
            return render_template(
                '/credential_profile/manage.html',
                form=form,
                profiles=profiles)
        elif _("Delete") in form_dict.values():
            message = _("Error - Profile can't be deleted")
            for key in form_dict.keys():
                if "delete" in key:
                    prof_id = int(key.replace("delete_", ""))
                    if delete_vc_profile_by_id(prof_id):
                        message = _("Profile deleted")
            form = ListProfileForm()
            return render_template(
                '/credential_profile/manage.html',
                form=form,
                message=message)
        else:
            return render_template(
                '/credential_profile/manage.html',
                form=form)


def render_profile(profile):
    profile_str = _("A {name} credential must :<br>").format(name=profile["profileName"])
    for item in profile["vcProfile"]:
        if item == "issuer":
            profile_str += _('<div style="margin-left: 40px">• be issued by {issuer}<br></div>').format(issuer=profile["vcProfile"][item])
        if item == "type":
            profile_str += _('<div style="margin-left: 40px">• be of type {type}<br></div>').format(type=profile["vcProfile"][item])
    return profile_str


@bp.route('/property_selection/create', methods=['GET', 'POST'])
def create_property_selection():
    properties = Property.query.all()
    properties_options = []
    for prop in properties:
        properties_options.append(prop.name)
    if request.method == 'GET':
        return render_template(
            '/property_selection/create.html',
            properties_options=properties_options)
    elif request.method == 'POST':
        request_dict = request.form.to_dict()
        print(request_dict)
        property_name = None
        properties_list = []
        nb_properties = 0
        for key in request_dict.keys():
            if "property_name" in key:
                property_name = request_dict[key]
            if "property_select" in key:
                nb_properties += 1
                if request_dict[key] is not "":
                    properties_list.append(request_dict[key])
        if property_name and len(properties_list) == nb_properties:
            properties = Property.query.all()
            statement_properties = []
            for prop in properties_list:
                for p in properties:
                    if p.name == prop:
                        statement_properties.append(p)
            new_statement = SdStatement(
                name=property_name,
                properties=statement_properties
            )
            db.session.add(new_statement)
            try:
                db.session.commit()
            except exc.SQLAlchemyError as error:
                if error.__str__().__contains__("UNIQUE constraint failed"):
                    message = _("Statement with name \"{property_name}\" already exists.").format(property_name=property_name)
                else:
                    message = _("Unknown Error")
                return render_template(
                    '/property_selection/create.html',
                    properties_options=properties_options,
                    message=message)
            message = _("Selective Disclosure Statement created")
            return render_template(
                '/property_selection/create.html',
                properties_options=properties_options,
                message=message)
        else:
            message = _("Please fill all parameters")
            return render_template(
                '/property_selection/create.html',
                properties_options=properties_options,
                message=message)


@bp.route('/property_selection/update', methods=['GET', 'POST'])
def update_property_selection():
    form_dict = request.form.to_dict()
    for key in form_dict.keys():
        if "modify" in key:
            statement_id = int(key.replace("modify_", ""))
            statement = read_sd_statement_by_id(statement_id)
            statement_name = statement["sdName"]
            properties = Property.query.all()
            properties_options = []
            requires = []
            for prop in properties:
                properties_options.append(prop.name)
            for prop in statement["requires"]:
                requires.append(prop)
            return render_template(
                '/property_selection/update.html',
                requires=requires,
                properties_options=properties_options,
                statement_name=statement_name,
                statement_id=statement_id)
    if request.method == 'POST':
        statement_name = None
        statement_id = None
        requires = []
        for key in form_dict.keys():
            if "property_name" in key:
                statement_name = form_dict[key]
            if "property_select" in key:
                requires.append(form_dict[key])
            if "statement_id" in key:
                statement_id = int(form_dict[key])
        if statement_name and statement_id and len(requires) > 0:
            if update_sd_statement_by_id(statement_name, requires, statement_id):
                message = _("Statement \"{statement_name}\" updated").format(statement_name=statement_name)
                form = ListPropertySelectionForm()
                return render_template(
                    '/property_selection/manage.html',
                    form=form,
                    message=message)
        message = _("Error: Statement \"{statement_name}\" could not be updated").format(statement_name=statement_name)
        form = ListPropertySelectionForm()
        return render_template(
            '/property_selection/manage.html',
            form=form,
            message=message)


@bp.route('/property_selection/manage', methods=['GET', 'POST'])
def manage_property_selection():
    form = ListPropertySelectionForm()
    if request.method == 'GET':
        return render_template(
            '/property_selection/manage.html',
            form=form)
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        if "prop_selection" in form_dict:
            if form_dict["prop_selection"] is not '':
                statements = []
                statement_dict = {}
                sd_statement = read_sd_statement_by_id(form_dict["prop_selection"])
                statement_dict["str"] = render_statement(sd_statement)
                statement_dict["id"] = form_dict["prop_selection"]
                statements.append(statement_dict)
                return render_template(
                    '/property_selection/manage.html',
                    form=form,
                    statements=statements)
            else:
                return render_template(
                    '/property_selection/manage.html',
                    form=form)
        elif "input_search_statement" in form_dict:
            input_str = form_dict["input_search_statement"]
            statements = []
            sd_statements = search_sd_statement_by_arg(input_str)
            for statement in sd_statements:
                statement_dict = dict()
                statement_dict["str"] = render_statement(statement.asdict())
                statement_dict["id"] = statement.id
                statements.append(statement_dict)
            return render_template(
                '/property_selection/manage.html',
                form=form,
                statements=statements)
        elif _("Delete") in form_dict.values():
            message = _("Error - Profile can't be deleted")
            for key in form_dict.keys():
                if "delete" in key:
                    stat_id = int(key.replace("delete_", ""))
                    if delete_sd_statement_by_id(stat_id):
                        message = _("Statement deleted")
            form = ListPropertySelectionForm()
            return render_template(
                '/property_selection/manage.html',
                form=form,
                message=message)


def render_statement(statement):
    statement_str = _("{sdName} requires :<br>").format(sdName=statement["sdName"])
    for item in statement["requires"]:
        statement_str += '<div style="margin-left: 40px">• ' + item + '<br></div>'
    return statement_str


@bp.route('/policy/create', methods=['GET', 'POST'])
def create_policy():
    form_dict = request.form.to_dict()
    profiles_options = []
    statements_options = []
    profiles = VcProfile.query.all()
    for profile in profiles:
        profiles_options.append(profile.name)
    statements = SdStatement.query.all()
    for statement in statements:
        statements_options.append(statement.name)
    if request.method == 'GET':
        return render_template(
            '/policy/create.html',
            statements_options=statements_options,
            profiles_options=profiles_options)
    if request.method == 'POST':
        if "select_either" in form_dict:
            print(form_dict["select_either"])
            print(form_dict["select_either"] ==  _("either"))
            if form_dict["select_either"] == _("either"):
                perform_action = form_dict["policy_perform_action_label"]
                resource_name = form_dict["resource_name"]
                policy = dict()
                policy["policyMatch"] = {}
                policy["policyMatch"]["action"] = perform_action
                policy["policyMatch"]["target"] = resource_name
                policy["cNLpolicy"] = {}
                policy["cNLpolicy"]["dnf"] = []
                cnf_dicts = fraction_dict(form_dict)
                for cnf_dict in cnf_dicts:
                    cnf_policy = dict()
                    cnf_policy["description"] = cnf_dict["description"]
                    cnf_policy["cnf"] = create_cnf_json_policy(cnf_dict)
                    policy["cNLpolicy"]["dnf"].append(cnf_policy)
                create_dnf_policy_from_json(policy)
            else:
                perform_action = form_dict["policy_perform_action_label"]
                resource_name = form_dict["resource_name"]
                cnf_policy = create_cnf_json_policy(form_dict)
                policy = dict()
                policy["policyMatch"] = {}
                policy["policyMatch"]["action"] = perform_action
                policy["policyMatch"]["target"] = resource_name
                policy["cNLpolicy"] = {}
                policy["cNLpolicy"]["cnf"] = cnf_policy
                create_cnf_policy_from_json(policy)
        return render_template(
            '/policy/create.html',
            statements_options=statements_options,
            profiles_options=profiles_options)


def fraction_dict(policy_dict):
    all_idx = []
    cnf_start_line = []
    for key in policy_dict.keys():
        if "description_line" in key:
            idx = int(key.replace("description_line", ""))
            cnf_start_line.append(idx)
        if key[-1].isdigit():
            key_idx = int(key[-1])
            if key_idx not in all_idx:
                all_idx.append(key_idx)
    all_idx.sort()
    cnf_start_line.append(all_idx[len(all_idx)-1]+1)
    cnf_dicts = []
    for i in range(0, len(cnf_start_line)-1):
        cnf_dict = dict()
        cnf_dict["description"] = policy_dict["description_line"+str(cnf_start_line[i])]
        for key in policy_dict.keys():
            if key[-1].isdigit():
                key_idx = int(key[-1])
                if cnf_start_line[i] <= key_idx < cnf_start_line[i+1]:
                    cnf_dict[key] = policy_dict[key]
        cnf_dicts.append(cnf_dict)
    return cnf_dicts


def create_cnf_json_policy(policy_dict):
    idx = 1
    for key in policy_dict.keys():
        if "description_line" in key:
            idx = int(key.replace("description_line", ""))
    line_cpt = idx
    lines = []
    while "statement_select_line" + str(line_cpt) in policy_dict:
        line = {}
        if "purpose_line" + str(line_cpt) in policy_dict:
            line["purpose"] = policy_dict["purpose_line" + str(line_cpt)]
        line["statement"] = policy_dict["statement_select_line" + str(line_cpt)]
        line["profile"] = policy_dict["profile_select_line" + str(line_cpt)]
        lines.append(line)
        line_cpt += 1
    cnf_policy = []
    temp = {}
    for line in lines:
        temp_or = {}
        if "purpose" in line:
            if bool(temp):
                cnf_policy.append(temp)
                temp = dict()
                temp["purpose"] = line["purpose"]
                temp["or"] = []
                temp_or["sdName"] = line["statement"]
                temp_or["profileName"] = line["profile"]
                temp["or"].append(temp_or)
            else:
                temp["purpose"] = line["purpose"]
                temp["or"] = []
                temp_or["sdName"] = line["statement"]
                temp_or["profileName"] = line["profile"]
                temp["or"].append(temp_or)
        else:
            temp_or["sdName"] = line["statement"]
            temp_or["profileName"] = line["profile"]
            temp["or"].append(temp_or)
    if bool(temp):
        cnf_policy.append(temp)
    return cnf_policy


@bp.route('/policy/manage', methods=['GET', 'POST'])
def manage_policy():
    form = ListPolicyForm()
    if request.method == 'GET':
        return render_template(
            '/policy/manage.html',
            form=form)
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        print(form_dict)
        if _("Get Policy in Json") in form_dict.values():
            for key in form_dict.keys():
                if "get_json" in key:
                    policy_match_id = int(key.replace("get_json_", ""))
                    json_policy = json.dumps(
                        read_policy_by_policy_match_id(policy_match_id).asdict(),
                        sort_keys=False,
                        indent=2)
                    return render_template(
                        '/policy/manage.html',
                        form=form,
                        json_policy=json_policy)
        if "policy" in form_dict:
            if form_dict["policy"] is not '':
                policies = []
                policy_dict = {}
                policy = read_policy_by_policy_match_id(form_dict["policy"])
                if "dnf" in policy.asdict()["cNLpolicy"]:
                    policy_dict["str"] = render_dnf_policy(policy.asdict())
                else:
                    policy_dict["str"] = render_cnf_policy(policy.asdict())
                policy_dict["id"] = policy.id
                policies.append(policy_dict)
                return render_template(
                    '/policy/manage.html',
                    form=form,
                    policies=policies)
            else:
                return render_template(
                    '/policy/manage.html',
                    form=form)
        elif "input_search_policy" in form_dict:
            input_str = form_dict["input_search_policy"]
            policies = []
            pols = search_policies_by_arg(input_str)
            for policy in pols:
                policy_dict = {}
                if "dnf" in policy.asdict()["cNLpolicy"]:
                    policy_dict["str"] = render_dnf_policy(policy.asdict())
                else:
                    policy_dict["str"] = render_cnf_policy(policy.asdict())
                policy_dict["id"] = policy.id
                policies.append(policy_dict)
            return render_template(
                '/policy/manage.html',
                form=form,
                policies=policies)
        elif _("Delete") in form_dict.values():
            message = _("Error - Policy can't be deleted")
            for key in form_dict.keys():
                if "delete" in key:
                    policy_match_id = int(key.replace("delete_", ""))
                    delete_policy_by_policy_match_id(policy_match_id)
                    message = _("Policy deleted")
            form = ListPolicyForm()
            return render_template(
                '/policy/manage.html',
                form=form,
                message=message)
        else:
            return render_template(
                '/policy/manage.html',
                form=form)


@bp.route('/policy/update', methods=['GET', 'POST'])
def update_policy():
    form_dict = request.form.to_dict()
    print("DICT", form_dict)
    dnf = []
    statements = SdStatement.query.all()
    statements_options = []
    for statement in statements:
        statements_options.append(statement.name)
    profiles = VcProfile.query.all()
    profiles_options = []
    for profile in profiles:
        profiles_options.append(profile.name)
    for key in form_dict.keys():
        if "modify" in key:
            policy_id = int(key.replace("modify_", ""))
            policy = Policies.query.filter(
                Policies.id == policy_id
            ).first()
            action = policy.policy_match.action
            target = policy.policy_match.target
            if policy.cnl_policy.cnf:
                select_either = "blank"
                select_options = [_("or"), _(") and"), ")"]
                cnf = []
                for j in range(0, len(policy.cnl_policy.cnf.and_nodes)):
                    and_node = policy.cnl_policy.cnf.and_nodes[j]
                    temp_and = dict()
                    temp_and["purpose"] = and_node.purpose
                    temp_and["policies"] = []
                    for k in range(0, len(and_node.or_node.policies)):
                        or_node_policy = and_node.or_node.policies[k]
                        temp_policy = dict()
                        temp_policy["statement"] = or_node_policy.statement.name
                        temp_policy["profile"] = or_node_policy.profile.name
                        if k < (len(and_node.or_node.policies)-1):
                            temp_policy["select"] = "or"
                        elif j == (len(policy.cnl_policy.cnf.and_nodes)-1):
                            temp_policy["select"] = ")"
                        elif k == (len(and_node.or_node.policies)-1):
                            temp_policy["select"] = ") and"
                        temp_and["policies"].append(temp_policy)
                    cnf.append(temp_and)
                return render_template(
                    '/policy/update.html',
                    action=action,
                    target=target,
                    select_either=select_either,
                    cnf=cnf,
                    statements_options=statements_options,
                    profiles_options=profiles_options,
                    select_options=select_options,
                    policy_id=policy_id)
            if policy.cnl_policy.dnf:
                select_either = "either"
                select_options = [_("or"), _(") and"), "))", _(")or(")]
                cnf_policies = policy.cnl_policy.dnf.cnf_policies
                for i in range(0, len(cnf_policies)):
                    cnf_policy = cnf_policies[i]
                    temp_dnf = dict()
                    temp_dnf["description"] = policy.cnl_policy.dnf.descriptions[i].description
                    temp_dnf["cnf_policy"] = []
                    for j in range(0, len(cnf_policy.and_nodes)):
                        and_node = cnf_policy.and_nodes[j]
                        temp_and = dict()
                        temp_and["purpose"] = and_node.purpose
                        temp_and["policies"] = []
                        for k in range(0, len(and_node.or_node.policies)):
                            or_node_policy = and_node.or_node.policies[k]
                            temp_policy = dict()
                            temp_policy["statement"] = or_node_policy.statement.name
                            temp_policy["profile"] = or_node_policy.profile.name
                            if k < (len(and_node.or_node.policies)-1):
                                temp_policy["select"] = "or"
                            elif i == (len(cnf_policies)-1):
                                temp_policy["select"] = "))"
                            elif j == (len(cnf_policy.and_nodes)-1):
                                temp_policy["select"] = ")or("
                            elif k == (len(and_node.or_node.policies)-1):
                                temp_policy["select"] = ") and"
                            temp_and["policies"].append(temp_policy)
                        temp_dnf["cnf_policy"].append(temp_and)
                    dnf.append(temp_dnf)
                return render_template(
                    '/policy/update.html',
                    action=action,
                    target=target,
                    select_either=select_either,
                    dnf=dnf,
                    statements_options=statements_options,
                    profiles_options=profiles_options,
                    select_options=select_options,
                    policy_id=policy_id)
    if request.method == 'POST':
        if "select_either" in form_dict:
            if form_dict["select_either"] == _("either"):
                policy_id = form_dict["policy_id"]
                print("ID", policy_id)
                perform_action = form_dict["policy_perform_action_label"]
                resource_name = form_dict["resource_name"]
                policy = dict()
                policy["policyMatch"] = {}
                policy["policyMatch"]["action"] = perform_action
                policy["policyMatch"]["target"] = resource_name
                policy["cNLpolicy"] = {}
                policy["cNLpolicy"]["dnf"] = []
                cnf_dicts = fraction_dict(form_dict)
                for cnf_dict in cnf_dicts:
                    cnf_policy = dict()
                    cnf_policy["description"] = cnf_dict["description"]
                    cnf_policy["cnf"] = create_cnf_json_policy(cnf_dict)
                    policy["cNLpolicy"]["dnf"].append(cnf_policy)
                    update_policy_by_id(policy_id, policy)
            else:
                policy_id = form_dict["policy_id"]
                print("ID", policy_id)
                perform_action = form_dict["policy_perform_action_label"]
                resource_name = form_dict["resource_name"]
                cnf_policy = create_cnf_json_policy(form_dict)
                policy = dict()
                policy["policyMatch"] = {}
                policy["policyMatch"]["action"] = perform_action
                policy["policyMatch"]["target"] = resource_name
                policy["cNLpolicy"] = {}
                policy["cNLpolicy"]["cnf"] = cnf_policy
                update_policy_by_id(policy_id, policy)
        form = ListPolicyForm()
        message = _("Policy updated")
        return render_template(
            '/policy/manage.html',
            form=form,
            message=message)


def render_cnf_policy(policy):
    policy_str = _("In order to ")
    policy_str += policy["policyMatch"]["action"]+" "
    policy_str += policy["policyMatch"]["target"]+" "
    policy_str += _("you must present ")
    cnf_node_cpt = 1
    cnf_node_len = len(policy["cNLpolicy"]["cnf"])
    for cnf_node in policy["cNLpolicy"]["cnf"]:
        if "purpose" in cnf_node.keys():
            policy_str += _(" for ")
            policy_str += cnf_node["purpose"]+" "
        policy_str += "( "
        or_node_cpt = 1
        or_node_len = len(cnf_node["or"])
        for or_node in cnf_node["or"]:
            policy_str += or_node["sdName"]+" "
            policy_str += _("from a ")
            policy_str += or_node["profileName"]+" "
            if or_node_len > or_node_cpt:
                policy_str += _("or ")
            else:
                policy_str += ") "
            or_node_cpt += 1
        if cnf_node_len > cnf_node_cpt:
            policy_str += _("and ")
        cnf_node_cpt += 1
    return policy_str


def render_dnf_policy(policy):
    policy_str = _("In order to ")
    policy_str += policy["policyMatch"]["action"]+" "
    policy_str += policy["policyMatch"]["target"]+" "
    policy_str += _("you must present either (")
    dnf_node_cpt = 1
    dnf_node_len = len(policy["cNLpolicy"]["dnf"])
    for dnf_node in policy["cNLpolicy"]["dnf"]:
        print(dnf_node)
        if dnf_node["description"] is not '':
            policy_str += dnf_node["description"]+" "
            policy_str += _("being ")
        cnf_node_cpt = 1
        cnf_node_len = len(dnf_node["cnf"])
        for cnf_node in dnf_node["cnf"]:
            or_node_cpt = 1
            or_node_len = len(cnf_node["or"])
            if "purpose" in cnf_node.keys():
                policy_str += cnf_node["purpose"]+" "
            policy_str += "( "
            for or_node in cnf_node["or"]:
                policy_str += or_node["sdName"]+" "
                policy_str += _("from a ")
                policy_str += or_node["profileName"]+" "
                if or_node_len > or_node_cpt:
                    policy_str += _("or ")
                or_node_cpt += 1
            policy_str += ") "
            if cnf_node_len > cnf_node_cpt:
                policy_str += _("and for ")
            cnf_node_cpt += 1
        if dnf_node_len > dnf_node_cpt:
            policy_str += _(") or (")
        dnf_node_cpt += 1
    policy_str += ")"
    return policy_str


@bp.route('/schema/upload', methods=['GET', 'POST'])
def upload_schema():
    form_dict = request.form.to_dict()
    if request.method == 'POST':
        extract_nested_properties = False
        if "nested_properties" in form_dict:
            extract_nested_properties = True
        if request.files["file"] is not "":
            json_file = request.files.get('file')
            json_file_data = json_file.read()
            json_schema = json.loads(json_file_data)
            get_schema_by_json_data(json_schema, extract_nested_properties)
        if "schema_url" in form_dict.keys():
            if form_dict["schema_url"] is not '':
                get_schema_by_url(form_dict["schema_url"], extract_nested_properties)
    return render_template('schema/upload.html')