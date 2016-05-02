import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.report.interfaces import IReport
import reports
from routes.mapper import SubMapper


class StatsresourcesPlugin(plugins.SingletonPlugin):
    """Plugin class."""

    plugins.implements(plugins.IConfigurer)
    plugins.implements(IReport)
    plugins.implements(plugins.IRoutes, inherit=True)

    def before_map(self, map):
        report_ctlr = 'ckanext.statsresources.controllers:StatsresourcesController'
        with SubMapper(map, controller=report_ctlr, action='recheck_access') as m:
            m.connect('reports', '/report', original_action='index')
            m.connect('report', '/report/:report_name', original_action='view')
            m.connect('report-org', '/report/:report_name/:organization',
                      original_action='view')
        return map

    # IConfigurer

    def update_config(self, config_):
        """Update instance config."""
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'statsresources')

    # IReport

    def register_reports(self):
        """Add custom reports."""
        return reports.stats_reports_info
