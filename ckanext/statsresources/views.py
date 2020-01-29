import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from flask import Blueprint


statsresources = Blueprint("statsresources", __name__)


def get_blueprints():
    return [statsresources]


def recheck_access(original_action, report_name=None, organization=None):
    strict_access = toolkit.asbool(toolkit.config.get("reports.strict_access"))
    if strict_access:
        context = {
            "model": model,
            "user": tookit.c.user,
            "auth_user_obj": tookit.c.userobj,
        }
        try:
            toolkit.check_access("sysadmin", context, {})
        except logic.NotAuthorized:
            tookit.abort(
                401, toolkit._("Need to be system administrator to administer"),
            )
    args = {}
    if report_name:
        args.update(report_name=report_name)
    if organization:
        args.update(organization=organization)
    return getattr(super(StatsresourcesController, self), original_action)(**args)


statsresources.add_url_rule(
    "/report", defaults=dict(original_action="index"), view_func=recheck_access
)
statsresources.add_url_rule(
    "/report/<report_name>",
    defaults=dict(original_action="view"),
    view_func=recheck_access,
)

statsresources.add_url_rule(
    "/report/<report_name>/<organization>",
    defaults=dict(original_action="view"),
    view_func=recheck_access,
)
