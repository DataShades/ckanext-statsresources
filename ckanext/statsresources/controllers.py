from ckanext.report.controllers import ReportController
import ckan.logic as logic
import ckan.model as model

import ckan.plugins.toolkit as toolkit
import ckan.lib.base as base
from pylons import config


class StatsresourcesController(ReportController):

    def recheck_access(self, original_action, report_name=None, organization=None):
        strict_access = toolkit.asbool(config.get('reports.strict_access'))
        if strict_access:
            context = {
                'model': model,
                'user': base.c.user,
                'auth_user_obj': base.c.userobj}
            try:
                logic.check_access('sysadmin', context, {})
            except logic.NotAuthorized:
                base.abort(401, base._(
                    'Need to be system administrator to administer'))
        args = {}
        if report_name:
            args.update(report_name=report_name)
        if organization:
            args.update(organization=organization)
        return getattr(super(StatsresourcesController, self), original_action)(
            **args
        )
