from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, SubmitField
from flask_babel import _
from .models import SdStatement, VcProfile, PolicyMatch, Schema


class ListPropertySelectionForm(FlaskForm):
    prop_selection = SelectField(render_kw={"class": "form-control", "onchange": "this.form.submit()"})

    def __init__(self):
        super(ListPropertySelectionForm, self).__init__()
        self.prop_selection.choices = []
        self.prop_selection.choices.append(('', _('please select an option')))
        for c in SdStatement.query.all():
            self.prop_selection.choices.append((c.id, c.name))


class PropertySelectionForm(FlaskForm):
    property_selection_name_str = _('Enter your name for property selection')
    requires_label_str = _('requires')
    list_of_properties_str = _('List of properties')
    property_selection_name = StringField(
        'property_selection_name',
        render_kw={"placeholder": property_selection_name_str, "style": "width: 310px;", "class": "form-control"})
    label = HiddenField(
        'label',
        default=requires_label_str)
    list_of_properties = SelectField(
        'list_of_properties',
        choices=[list_of_properties_str], render_kw={"class": "form-control"})
    plus_field = SubmitField(
        "Plus",
        render_kw={"class": "form-control"})
    minus_field = SubmitField(
        "Minus",
        render_kw={"class": "form-control"})


class PolicyForm(FlaskForm):
    label_par_str = _('(')
    label_from_str = _('from a')
    list_of_properties_str = _('List of properties')
    list_of_profiles_str = _('List of credential profiles')
    and_or_choices = [
        _('and, ), or'),
        _('and'),
        _(')'),
        _('or')]
    label_par = HiddenField(
        'label_par',
        default=label_par_str)
    list_of_properties = SelectField(
        'list_of_properties',
        choices=[list_of_properties_str],
        render_kw={"class": "form-control"})
    label_from = HiddenField(
        'label_from',
        default=label_from_str)
    list_of_profiles = SelectField(
        'list_of_profiles',
        choices=[list_of_profiles_str],
        render_kw={"class": "form-control"})
    and_or_select = SelectField(
        'and_or_select',
        choices=and_or_choices,
        render_kw={"class": "form-control", "onchange": "this.form.submit()"})


class ListProfileForm(FlaskForm):
    profile = SelectField(render_kw={"class": "form-control", "onchange": "this.form.submit()"})

    def __init__(self):
        super(ListProfileForm, self).__init__()
        self.profile.choices = []
        self.profile.choices.append(('', _('please select an option')))
        for c in VcProfile.query.all():
            self.profile.choices.append((c.id, c.name))


class ListPolicyForm(FlaskForm):
    policy = SelectField(render_kw={"class": "form-control", "onchange": "this.form.submit()"})

    def __init__(self):
        super(ListPolicyForm, self).__init__()
        self.policy.choices = []
        self.policy.choices.append(('', _('please select an option')))
        for c in PolicyMatch.query.all():
            self.policy.choices.append((c.id, c.action+" "+c.target))


class ListSchemaForm(FlaskForm):
    schema = SelectField(render_kw={"class": "form-control", "onchange": "this.form.submit()"})

    def __init__(self):
        super(ListSchemaForm, self).__init__()
        self.schema.choices = []
        self.schema.choices.append(('', _('please select an option')))
        for c in Schema.query.all():
            self.schema.choices.append((c.id, c.name))

