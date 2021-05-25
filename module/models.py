"""Data models."""
from . import db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Schema(db.Model):
    """Data  model for schemas."""

    __tablename__ = 'schema'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(64),
        index=False,
        unique=True,
        nullable=False
    )
    type_id = db.Column(db.Integer, db.ForeignKey('vc_type.id'))
    type = db.relationship("VcType", back_populates="schemas")
    issuer_id = db.Column(db.Integer, db.ForeignKey('issuer.id'))
    issuer = db.relationship("Issuer", back_populates="schemas")

    properties = db.relationship("Property", back_populates="schema")


class VcProfile(db.Model):
    """Data model for vc_profiles."""

    __tablename__ = 'vc_profile'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(64),
        index=False,
        unique=True,
        nullable=False
    )
    policy = db.relationship(
        "Policy",
        back_populates="profile"
    )
    type_id = db.Column(db.Integer, db.ForeignKey('vc_type.id'))
    type = db.relationship("VcType", back_populates="profiles")
    issuer_id = db.Column(db.Integer, db.ForeignKey('issuer.id'))
    issuer = db.relationship("Issuer", back_populates="profiles")

    def __repr__(self):
        return '<VcProfile {}>'.format(self.name)

    def asdict(self):
        return {'profileName': self.name,
                'vcProfile': {
                    'issuer': self.issuer.name,
                    'type': self.type.name}}


class Issuer(db.Model):
    """Data model for issuers."""

    __tablename__ = 'issuer'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(64),
        index=False,
        unique=True,
        nullable=False
    )
    profiles = db.relationship("VcProfile", back_populates="issuer")
    schemas = db.relationship("Schema", back_populates="issuer")

    def __repr__(self):
        return '<Issuer {}>'.format(self.name)


class VcType(db.Model):
    """Data model for vc_types."""

    __tablename__ = 'vc_type'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(64),
        index=False,
        unique=True,
        nullable=False
    )
    profiles = db.relationship("VcProfile", back_populates="type")
    schemas = db.relationship("Schema", back_populates="type")

    def __repr__(self):
        return '<VcType {}>'.format(self.name)


association_table = db.Table(
    'association',
    db.Model.metadata,
    db.Column('sd_statement_id', db.Integer, db.ForeignKey('sd_statement.id')),
    db.Column('property_id', db.Integer, db.ForeignKey('property.id'))
)


class SdStatement(db.Model):
    """Data model for sd_statements."""

    __tablename__ = 'sd_statement'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(64),
        index=False,
        unique=True
    )
    properties = db.relationship(
        "Property",
        secondary=association_table,
        back_populates="statements"
    )
    policy = db.relationship(
        "Policy",
        back_populates="statement"
    )

    def __repr__(self):
        return '<SdStatement {} {}>'.format(self.name, self.properties)

    def asdict(self):
        model_dict = dict()
        model_dict["sdName"] = self.name
        model_dict["requires"] = []
        for prop in self.properties:
            if prop.name == "all":
                model_dict["requires"].append("*")
            else:
                model_dict["requires"].append(prop.name)
        return model_dict


class Property(db.Model):
    """Data model for properties."""

    __tablename__ = 'property'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(256),
        index=False,
        nullable=False
    )
    statements = db.relationship(
        "SdStatement",
        secondary=association_table,
        back_populates="properties"
    )
    schema_id = db.Column(db.Integer, db.ForeignKey('schema.id'))
    schema = db.relationship("Schema", back_populates="properties")

    def __repr__(self):
        return '<Property {}>'.format(self.name)

    def __str__(self):
        return self.name


class Policies(db.Model):
    """Data model for policies."""

    __tablename__ = 'full_policies'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    policy_match_id = db.Column(
        db.Integer,
        db.ForeignKey('policy_match.id')
    )
    policy_match = db.relationship(
        "PolicyMatch",
        back_populates="full_policy"
    )
    cnl_policy_id = db.Column(
        db.Integer,
        db.ForeignKey('cnl_policies.id')
    )
    cnl_policy = db.relationship(
        "CnlPolicy",
        back_populates="full_policy"
    )

    def asdict(self):
        model_dict = self.policy_match.asdict()
        model_dict.update(self.cnl_policy.asdict())
        return model_dict


class PolicyMatch(db.Model):
    """Data model for policy matches."""

    __tablename__ = 'policy_match'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    action = db.Column(
        db.String(256),
        index=False,
        unique=False,
        nullable=False
    )
    target = db.Column(
        db.String(256),
        index=False,
        unique=False,
        nullable=False
    )
    full_policy = db.relationship(
        "Policies",
        back_populates="policy_match",
        uselist=False
    )
    __table_args__ = (db.UniqueConstraint('action', 'target', name='unique_policy_match_name'),)

    def asdict(self):
        return {"policyMatch": {
            "action": self.action,
            "target": self.target}
        }


class CnlPolicy(db.Model):
    """Data model for cnl policies."""

    __tablename__ = 'cnl_policies'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    cnf_id = db.Column(
        db.Integer,
        db.ForeignKey('cnf_policies.id')
    )
    cnf = db.relationship(
        "Cnf",
        back_populates="cnl_policy"
    )
    dnf_id = db.Column(
        db.Integer,
        db.ForeignKey('dnf_policies.id')
    )
    dnf = db.relationship(
        "Dnf",
        back_populates="cnl_policy"
    )
    full_policy = db.relationship(
        "Policies",
        back_populates="cnl_policy",
        uselist=False
    )

    def asdict(self):
        if self.cnf:
            return {"cNLpolicy": self.cnf.asdict()}
        elif self.dnf:
            return {"cNLpolicy": self.dnf.asdict()}


class Dnf(db.Model):
    """Data model for DNF Policies."""

    __tablename__ = 'dnf_policies'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    cnl_policy = db.relationship(
        "CnlPolicy",
        back_populates="dnf",
        uselist=False
    )
    cnf_policies = db.relationship("Cnf", back_populates="dnf")
    descriptions = db.relationship("Description", back_populates="dnf")

    def asdict(self):
        model_dict = {}
        if self.cnf_policies:
            model_dict["dnf"] = []
            for i in range(0, len(self.cnf_policies)):
                temp_dict = {"description": self.descriptions[i].description}
                temp_dict.update(self.cnf_policies[i].asdict())
                model_dict["dnf"].append(temp_dict)
        return model_dict


class Description(db.Model):
    """Data model for Description."""

    __tablename__ = 'description'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    description = db.Column(
        db.String(256),
        index=False,
        nullable=False
    )
    dnf_id = db.Column(
        db.Integer,
        db.ForeignKey('dnf_policies.id')
    )
    dnf = db.relationship(
        "Dnf",
        back_populates="descriptions"
    )


class Cnf(db.Model):
    """Data model for CNF policies."""

    __tablename__ = 'cnf_policies'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    cnl_policy = db.relationship(
        "CnlPolicy",
        back_populates="cnf",
        uselist=False
    )
    dnf_id = db.Column(
        db.Integer,
        db.ForeignKey('dnf_policies.id')
    )
    dnf = db.relationship(
        "Dnf",
        back_populates="cnf_policies"
    )
    and_nodes = db.relationship("AndNode", back_populates="cnf")

    def asdict(self):
        model_dict = {}
        if self.and_nodes:
            model_dict["cnf"] = []
            for and_node in self.and_nodes:
                model_dict["cnf"].append(and_node.asdict())
        return model_dict


class AndNode(db.Model):
    """Data model for And nodes."""

    __tablename__ = 'and_nodes'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    purpose = db.Column(
        db.String(256),
        index=False,
        nullable=True
    )
    cnf_id = db.Column(
        db.Integer,
        db.ForeignKey('cnf_policies.id')
    )
    cnf = db.relationship(
        "Cnf",
        back_populates="and_nodes"
    )
    or_node = db.relationship(
        "OrNode",
        back_populates="and_node",
        uselist=False)

    def asdict(self):
        model_dict = {}
        if self.purpose:
            model_dict["purpose"] = self.purpose
        if self.or_node.policies:
            model_dict["or"] = []
            for policy in self.or_node.policies:
                model_dict["or"].append(policy.asdict())
        return model_dict


class OrNode(db.Model):
    """Data model for Or nodes."""

    __tablename__ = 'or_nodes'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    and_node_id = db.Column(
        db.Integer,
        db.ForeignKey('and_nodes.id')
    )
    and_node = db.relationship(
        "AndNode",
        back_populates="or_node"
    )
    policies = db.relationship("Policy", back_populates="or_node")

    def asdict(self):
        model_dict = {}
        if self.policies:
            model_dict["or"] = []
            for policy in self.policies:
                model_dict["or"].append(policy.asdict())
        return model_dict


class Policy(db.Model):
    """Data model for Policies."""

    __tablename__ = 'policies'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    or_node_id = db.Column(
        db.Integer,
        db.ForeignKey('or_nodes.id')
    )
    or_node = db.relationship(
        "OrNode",
        back_populates="policies"
    )
    profile_id = db.Column(
        db.Integer,
        db.ForeignKey('vc_profile.id')
    )
    profile = db.relationship(
        "VcProfile",
        back_populates="policy"
    )
    statement_id = db.Column(
        db.Integer,
        db.ForeignKey('sd_statement.id')
    )
    statement = db.relationship(
        "SdStatement",
        back_populates="policy"
    )

    def asdict(self):
        return {'sdName': self.statement.name,
                'profileName': self.profile.name}
