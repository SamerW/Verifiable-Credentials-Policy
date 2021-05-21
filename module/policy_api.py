from flask import request, make_response, Response
from flask import current_app as app
from sqlalchemy import func
from .models import db, \
    Policy, \
    OrNode, \
    AndNode, \
    Cnf, \
    CnlPolicy, \
    PolicyMatch, \
    Dnf, \
    Description, \
    Policies
from flask_babel import _
import json
from sqlalchemy.exc import IntegrityError
from .profile_api import get_vc_profile
from .statement_api import get_sd_statement



@app.route('/v1/cnlpolicy/create', methods=['GET'])
def create_policy():
    """Create a policy via query string parameters."""
    b64_policy_match = request.args.get('policyMatch')
    policy_match = base64.urlsafe_b64decode(b64_policy_match)
    json_policy_match = json.loads(policy_match)
    b64_cnl_policy = request.args.get('cNLpolicy')
    cnl_policy = base64.urlsafe_b64decode(b64_cnl_policy)
    json_cnl_policy = json.loads(cnl_policy)
    json_data = {}
    json_data["policyMatch"] = json_policy_match
    json_data["cNLpolicy"] = json_cnl_policy
    if "cNLpolicy" in json_data:
        json_cnl_policy = json_data["cNLpolicy"]
        if "cnf" in json_cnl_policy:
            json_cnf_policy = json_cnl_policy["cnf"]
            and_nodes = []
            for json_and_node in json_cnf_policy:
                if "or" in json_and_node:
                    json_or_nodes = json_and_node["or"]
                    policies = []
                    for json_or_node in json_or_nodes:
                        sd_name = json_or_node["sdName"]
                        profile_name = json_or_node["profileName"]
                        policy = Policy()
                        policy.profile = get_vc_profile(profile_name)
                        policy.statement = get_sd_statement(sd_name)
                        policies.append(policy)
                    or_node = OrNode(policies=policies)
                    purpose = None
                    if "purpose" in json_and_node:
                        purpose = json_and_node["purpose"]
                    and_node = AndNode(purpose=purpose, or_node=or_node)
                    and_nodes.append(and_node)
            cnf = Cnf(and_nodes=and_nodes)
            cnl_policy = CnlPolicy(cnf=cnf)
            action = json_data["policyMatch"]["action"]
            target = json_data["policyMatch"]["target"]
            policy_match = PolicyMatch(action=action, target=target)
            final_policy = policy_match.asdict()
            final_policy.update(cnl_policy.asdict())
            policy_result = create_cnf_policy_from_json(final_policy)
            if policy_result == _("Policy already exists"):
                return Response(status=409)
            elif policy_result == True:
                return Response(status=200)
        if "dnf" in json_cnl_policy:
            json_dnf_policy = json_cnl_policy["dnf"]
            cnf_policies = []
            descriptions = []
            for json_dnf_or_node in json_dnf_policy:
                if "cnf" in json_dnf_or_node:
                    json_cnf_policy = json_dnf_or_node["cnf"]
                    and_nodes = []
                    for json_and_node in json_cnf_policy:
                        if "or" in json_and_node:
                            json_or_nodes = json_and_node["or"]
                            policies = []
                            for json_or_node in json_or_nodes:
                                sd_name = json_or_node["sdName"]
                                profile_name = json_or_node["profileName"]
                                policy = Policy()
                                policy.profile = get_vc_profile(profile_name)
                                policy.statement = get_sd_statement(sd_name)
                                policies.append(policy)
                            or_node = OrNode(policies=policies)
                            if "purpose" in json_and_node:
                                purpose = json_and_node["purpose"]
                                and_node = AndNode(purpose=purpose, or_node=or_node)
                                and_nodes.append(and_node)
                            else:
                                and_node = AndNode(or_node=or_node)
                                and_nodes.append(and_node)
                    cnf = Cnf(and_nodes=and_nodes)
                    cnf_policies.append(cnf)
                    description = Description(description=json_dnf_or_node["description"])
                    descriptions.append(description)
            dnf = Dnf(cnf_policies=cnf_policies, descriptions=descriptions)
            cnl_policy = CnlPolicy(dnf=dnf)
            action = json_data["policyMatch"]["action"]
            target = json_data["policyMatch"]["target"]
            policy_match = PolicyMatch(action=action, target=target)
            final_policy = Policies(policy_match=policy_match, cnl_policy=cnl_policy)
            policy_result = create_dnf_policy_from_json(final_policy)
            if policy_result == _("Policy already exists"):
                return Response(status=409)
            elif policy_result == True:
                return Response(status=200)
    return Response(status=400)


def create_cnf_policy():
    """Create a policy via query string parameters."""
    json_str = """
    {
        "policyMatch": {
            "action": "purchase",
            "target": "a car parking permit" 
        },
        "cNLpolicy": { 
            "cnf": [{
                "purpose": "proving your address",
                "or": [{
                    "sdName": "Name and Address",
                    "profileName": "residency permit"
                }, {
                    "sdName": "Name and Address", 
                    "profileName": "utility bill"
                }] 
            }]
        }
    }"""
    json_data = json.loads(json_str)
    if "cNLpolicy" in json_data:
        json_cnl_policy = json_data["cNLpolicy"]
        if "cnf" in json_cnl_policy:
            json_cnf_policy = json_cnl_policy["cnf"]
            and_nodes = []
            for json_and_node in json_cnf_policy:
                if "or" in json_and_node:
                    json_or_nodes = json_and_node["or"]
                    policies = []
                    for json_or_node in json_or_nodes:
                        sd_name = json_or_node["sdName"]
                        profile_name = json_or_node["profileName"]
                        policy = Policy()
                        policy.profile = get_vc_profile(profile_name)
                        policy.statement = get_sd_statement(sd_name)
                        policies.append(policy)
                    or_node = OrNode(policies=policies)
                    purpose = None
                    if "purpose" in json_and_node:
                        purpose = json_and_node["purpose"]
                    and_node = AndNode(purpose=purpose, or_node=or_node)
                    and_nodes.append(and_node)
            cnf = Cnf(and_nodes=and_nodes)
            cnl_policy = CnlPolicy(cnf=cnf)
            action = json_data["policyMatch"]["action"]
            target = json_data["policyMatch"]["target"]
            policy_match = PolicyMatch(action=action, target=target)
            final_policy = policy_match.asdict()
            final_policy.update(cnl_policy.asdict())
            return json.dumps(final_policy, indent=4)
    return json_data


def create_cnf_policy_from_json(json_data):
    """Create a policy via json parameter."""
    if "cNLpolicy" in json_data:
        json_cnl_policy = json_data["cNLpolicy"]
        if "cnf" in json_cnl_policy:
            json_cnf_policy = json_cnl_policy["cnf"]
            and_nodes = []
            for json_and_node in json_cnf_policy:
                if "or" in json_and_node:
                    json_or_nodes = json_and_node["or"]
                    policies = []
                    for json_or_node in json_or_nodes:
                        sd_name = json_or_node["sdName"]
                        profile_name = json_or_node["profileName"]
                        policy = Policy()
                        policy.profile = get_vc_profile(profile_name)
                        policy.statement = get_sd_statement(sd_name)
                        policies.append(policy)
                    or_node = OrNode(policies=policies)
                    purpose = None
                    if "purpose" in json_and_node:
                        purpose = json_and_node["purpose"]
                    and_node = AndNode(purpose=purpose, or_node=or_node)
                    and_nodes.append(and_node)
            cnf = Cnf(and_nodes=and_nodes)
            cnl_policy = CnlPolicy(cnf=cnf)
            action = json_data["policyMatch"]["action"]
            target = json_data["policyMatch"]["target"]
            policy_match = PolicyMatch(action=action, target=target)
            final_policy = Policies(policy_match=policy_match, cnl_policy=cnl_policy)
            try:
                db.session.add(final_policy)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return _("Policy already exists")
            return True


def create_dnf_policy():
    """Create a policy via query string parameters."""
    json_str = """
    {
        "policyMatch": {
            "action": "be",
            "target": "over 19"
        },
        "cNLpolicy": {
            "dnf": [{
                "description": "Proof of Age",
                "cnf": [{
                    "purpose": "N.B. not needed in this example",
                    "or": [{
                        "sdName": "Name and Address",
                        "profileName": "residency permit"
                    }]
                }]
            }, {
                "description": "Proof of Date of Birth",
                "cnf": [{
                    "or": [{
                        "sdName": "Name and Address",
                        "profileName": "utility bill"
                    }]
                }]
            }]
        }
    }"""
    json_data = json.loads(json_str)
    if "cNLpolicy" in json_data:
        json_cnl_policy = json_data["cNLpolicy"]
        if 'dnf' in json_cnl_policy:
            json_dnf_policy = json_cnl_policy["dnf"]
            cnf_policies = []
            descriptions = []
            for json_dnf_or_node in json_dnf_policy:
                if "cnf" in json_dnf_or_node:
                    json_cnf_policy = json_dnf_or_node["cnf"]
                    and_nodes = []
                    for json_and_node in json_cnf_policy:
                        if "or" in json_and_node:
                            json_or_nodes = json_and_node["or"]
                            policies = []
                            for json_or_node in json_or_nodes:
                                sd_name = json_or_node["sdName"]
                                profile_name = json_or_node["profileName"]
                                policy = Policy()
                                policy.profile = get_vc_profile(profile_name)
                                policy.statement = get_sd_statement(sd_name)
                                policies.append(policy)
                            or_node = OrNode(policies=policies)
                            if "purpose" in json_and_node:
                                purpose = json_and_node["purpose"]
                                and_node = AndNode(purpose=purpose, or_node=or_node)
                                and_nodes.append(and_node)
                            else:
                                and_node = AndNode(or_node=or_node)
                                and_nodes.append(and_node)
                    cnf = Cnf(and_nodes=and_nodes)
                    cnf_policies.append(cnf)
                    description = Description(description=json_dnf_or_node["description"])
                    descriptions.append(description)
            dnf = Dnf(cnf_policies=cnf_policies, descriptions=descriptions)
            cnl_policy = CnlPolicy(dnf=dnf)
            action = json_data["policyMatch"]["action"]
            target = json_data["policyMatch"]["target"]
            policy_match = PolicyMatch(action=action, target=target)
            final_policy = Policies(policy_match=policy_match, cnl_policy=cnl_policy)
            return json.dumps(final_policy, indent=4)
    return json_data


def create_dnf_policy_from_json(json_data):
    """Create a policy via json parameter."""
    if "cNLpolicy" in json_data:
        json_cnl_policy = json_data["cNLpolicy"]
        if 'dnf' in json_cnl_policy:
            json_dnf_policy = json_cnl_policy["dnf"]
            cnf_policies = []
            descriptions = []
            for json_dnf_or_node in json_dnf_policy:
                if "cnf" in json_dnf_or_node:
                    json_cnf_policy = json_dnf_or_node["cnf"]
                    and_nodes = []
                    for json_and_node in json_cnf_policy:
                        if "or" in json_and_node:
                            json_or_nodes = json_and_node["or"]
                            policies = []
                            for json_or_node in json_or_nodes:
                                sd_name = json_or_node["sdName"]
                                profile_name = json_or_node["profileName"]
                                policy = Policy()
                                policy.profile = get_vc_profile(profile_name)
                                policy.statement = get_sd_statement(sd_name)
                                policies.append(policy)
                            or_node = OrNode(policies=policies)
                            if "purpose" in json_and_node:
                                purpose = json_and_node["purpose"]
                                and_node = AndNode(purpose=purpose, or_node=or_node)
                                and_nodes.append(and_node)
                            else:
                                and_node = AndNode(or_node=or_node)
                                and_nodes.append(and_node)
                    cnf = Cnf(and_nodes=and_nodes)
                    cnf_policies.append(cnf)
                    description = Description(description=json_dnf_or_node["description"])
                    descriptions.append(description)
            dnf = Dnf(cnf_policies=cnf_policies, descriptions=descriptions)
            cnl_policy = CnlPolicy(dnf=dnf)
            action = json_data["policyMatch"]["action"]
            target = json_data["policyMatch"]["target"]
            policy_match = PolicyMatch(action=action, target=target)
            final_policy = Policies(policy_match=policy_match, cnl_policy=cnl_policy)
            try:
                db.session.add(final_policy)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return _("Policy already exists")
            return True
            #return make_response(final_policy.asdict())
    return _("Json Error")


@app.route('/v1/cnlpolicy/read', methods=['GET'])
def read_policy():
    """Read a policy via query string parameters."""
    target = request.args.get('target')
    action = request.args.get('action')
    if target and action:
        existing_policy_match = PolicyMatch.query.filter(
            PolicyMatch.target == target,
            PolicyMatch.action == action
        ).first()
        if existing_policy_match:
            existing_policy = Policies.query.filter(
                Policies.policy_match_id == existing_policy_match.id
            ).first()
            if existing_policy:
                res = json.dumps(existing_policy.asdict(),
                                 sort_keys=False,
                                 indent=2)
                return Response(res, content_type='application/json', status=200)
            else:
                return Response(status=404)
        else:
            return Response(status=404)
    else:
        return Response(status=404)


def read_policy_by_policy_match_id(policy_match_id):
    existing_policy_match = PolicyMatch.query.filter(
        PolicyMatch.id == policy_match_id
    ).first()
    if existing_policy_match:
        existing_policy = Policies.query.filter(
            Policies.policy_match_id == existing_policy_match.id
        ).first()
        if existing_policy:
            return existing_policy
        else:
            return make_response(_("Policy with PolicyMatchId {policy_match_id} doesn't exist").format(policy_match_id=str(policy_match_id)))
    else:
        return make_response(_("Policy with PolicyMatchId {policy_match_id} doesn't exist").format(policy_match_id=str(policy_match_id)))


@app.route('/v1/cnlpolicy/update', methods=['GET'])
def update_policy():
    """update a policy via query string parameters."""
    b64_policy_match = request.args.get('policyMatch')
    policy_match = base64.urlsafe_b64decode(b64_policy_match)
    json_policy_match = json.loads(policy_match)
    b64_cnl_policy = request.args.get('cNLpolicy')
    cnl_policy = base64.urlsafe_b64decode(b64_cnl_policy)
    json_cnl_policy = json.loads(cnl_policy)
    json_data = {}
    json_data["policyMatch"] = json_policy_match
    json_data["cNLpolicy"] = json_cnl_policy
    if json_policy_match and json_cnl_policy:
        existing_policy_match = PolicyMatch.query.filter(
            PolicyMatch.target == json_policy_match["target"],
            PolicyMatch.action == json_policy_match["action"]
        ).first()
        if existing_policy_match:
            existing_policy = Policies.query.filter(
                Policies.policy_match_id == existing_policy_match.id
            ).first()
            if existing_policy:
                update_policy_by_id(existing_policy.id, json_data)
                return Response(status=200)
            else:
                return Response(status=400)
        else:
            if "cnf" in json_cnl_policy:
                create_cnf_policy_from_json(json_data)
                return Response(status=200)
            elif "dnf" in json_cnl_policy:
                create_dnf_policy_from_json(json_data)
                return Response(status=200)
            else:
                return Response(status=400)
    else:
        return Response(status=400)


def update_policy_by_id(policy_id, policy):
    """update a policy via parameters."""
    existing_policy = Policies.query.filter(
        Policies.id == policy_id
    ).first()
    if existing_policy:
        delete_policy_by_policy_match_id(existing_policy.policy_match.id)
        if "dnf" in policy["cNLpolicy"]:
            create_dnf_policy_from_json(policy)
        if "cnf" in policy["cNLpolicy"]:
            create_cnf_policy_from_json(policy)
    else:
        return make_response(_("Policy with id {policy_id} doesn't exist").format(policy_id=policy_id))


@app.route('/v1/cnlpolicy/delete', methods=['GET'])
def delete_policy():
    """delete a policy via query string parameters."""
    target = request.args.get('target')
    action = request.args.get('action')
    if target and action:
        existing_policy_match = PolicyMatch.query.filter(
            PolicyMatch.target == target,
            PolicyMatch.action == action
        ).first()
        if existing_policy_match:
            delete_policy_by_policy_match_id(existing_policy_match.id)
            return Response(status=200)
        else:
            return Response(status=400)
    else:
        return Response(status=400)


def delete_policy_by_policy_match_id(policy_match_id):
    existing_policy = Policies.query.filter(
        Policies.policy_match_id == policy_match_id
    ).first()
    db.session.delete(existing_policy.policy_match)
    if existing_policy.cnl_policy.dnf:
        for description in existing_policy.cnl_policy.dnf.descriptions:
            db.session.delete(description)
        for cnf_policy in existing_policy.cnl_policy.dnf.cnf_policies:
            for and_node in cnf_policy.and_nodes:
                for policy in and_node.or_node.policies:
                    db.session.delete(policy)
                db.session.delete(and_node.or_node)
                db.session.delete(and_node)
            db.session.delete(cnf_policy)
        db.session.delete(existing_policy.cnl_policy.dnf)
        db.session.delete(existing_policy.cnl_policy)
        db.session.delete(existing_policy)
    else:
        for and_node in existing_policy.cnl_policy.cnf.and_nodes:
            for policy in and_node.or_node.policies:
                db.session.delete(policy)
            db.session.delete(and_node.or_node)
            db.session.delete(and_node)
        db.session.delete(existing_policy.cnl_policy.cnf)
        db.session.delete(existing_policy.cnl_policy)
        db.session.delete(existing_policy)
    db.session.commit()


@app.route('/v1/cnlpolicy/search', methods=['GET'])
def search_policy():
    """search a policy via query string parameters."""
    b64_policy_match = request.args.get('policyMatch')
    b64_cnl_policy = request.args.get('cNLpolicy')
    if b64_policy_match and b64_cnl_policy:
        policy_match_str = base64.urlsafe_b64decode(b64_policy_match)
        cnl_policy_str = base64.urlsafe_b64decode(b64_cnl_policy)
        all_matchable_policies = []
        policies = []
        existing_policy_match = PolicyMatch.query.filter(
            func.lower(PolicyMatch.target.contains(func.lower(policy_match_str))) |
            func.lower(PolicyMatch.action.contains(func.lower(policy_match_str)))
        ).all()
        if existing_policy_match:
            for policy_match in existing_policy_match:
                existing_policy = Policies.query.filter(
                    Policies.policy_match_id == policy_match.id
                ).first()
                if existing_policy:
                    all_matchable_policies.append(existing_policy)
        for policy in all_matchable_policies:
            policy_object_str = get_all_policy_object_str(policy)
            is_contained = False
            for item in policy_object_str:
                lower_cnl_policy_str = cnl_policy_str.lower()
                lower_item = item.lower()
                if lower_cnl_policy_str in lower_item:
                    is_contained = True
            if is_contained:
                policies.append(policy.asdict())
        response = {"policies": policies}
        res = json.dumps(response,
                         sort_keys=False,
                         indent=2)
        return Response(res, content_type='application/json', status=200)
    elif b64_policy_match:
        policy_match_str = base64.urlsafe_b64decode(b64_policy_match)
        policies = []
        existing_policy_match = PolicyMatch.query.filter(
            func.lower(PolicyMatch.target.contains(func.lower(policy_match_str))) |
            func.lower(PolicyMatch.action.contains(func.lower(policy_match_str)))
        ).all()
        if existing_policy_match:
            for policy_match in existing_policy_match:
                existing_policy = Policies.query.filter(
                    Policies.policy_match_id == policy_match.id
                ).first()
                if existing_policy:
                    policies.append(existing_policy.asdict())
        response = {"policies": policies}
        res = json.dumps(response,
                         sort_keys=False,
                         indent=2)
        return Response(res, content_type='application/json', status=200)
    elif b64_cnl_policy:
        cnl_policy_str = base64.urlsafe_b64decode(b64_cnl_policy)
        policies = []
        all_policies = Policies.query.all()
        for policy in all_policies:
            policy_object_str = get_all_policy_object_str(policy)
            is_contained = False
            for item in policy_object_str:
                lower_cnl_policy_str = cnl_policy_str.lower()
                lower_item = item.lower()
                if lower_cnl_policy_str in lower_item:
                    is_contained = True
            if is_contained:
                policies.append(policy.asdict())
        response = {"policies": policies}
        res = json.dumps(response,
                         sort_keys=False,
                         indent=2)
        return Response(res, content_type='application/json', status=200)
    else:
        policies = []
        all_policies = Policies.query.all()
        for policy in all_policies:
            policies.append(policy.asdict())
        response = {"policies": policies}
        res = json.dumps(response,
                         sort_keys=False,
                         indent=2)
        return Response(res, content_type='application/json', status=200)

def search_policies_by_arg(pol_str):
    """search a policy via arg."""
    policies = []
    all_policies = Policies.query.all()
    for policy in all_policies:
        policy_object_str = get_all_policy_object_str(policy)
        is_contained = False
        for item in policy_object_str:
            lower_pol_str = pol_str.lower()
            lower_item = item.lower()
            if lower_pol_str in lower_item:
                is_contained = True
        if is_contained:
            policies.append(policy)
    return policies


def get_all_policy_object_str(policy):
    policy_str = [policy.policy_match.action, policy.policy_match.target]
    cnl_policy = policy.cnl_policy
    if cnl_policy.cnf:
        for and_node in cnl_policy.cnf.and_nodes:
            if and_node.purpose:
                policy_str.append(and_node.purpose)
            for policy in and_node.or_node.policies:
                policy_str.append(policy.statement.name)
                policy_str.append(policy.profile.name)
    if cnl_policy.dnf:
        for description in cnl_policy.dnf.descriptions:
            policy_str.append(description.description)
        cnfs = cnl_policy.dnf.cnf_policies
        for cnf_policy in cnfs:
            for and_node in cnf_policy.and_nodes:
                if and_node.purpose:
                    policy_str.append(and_node.purpose)
                for policy in and_node.or_node.policies:
                    policy_str.append(policy.profile.name)
                    policy_str.append(policy.statement.name)
    return policy_str
