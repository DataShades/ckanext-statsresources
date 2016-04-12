import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.report.interfaces import IReport
import reports


class StatsresourcesPlugin(plugins.SingletonPlugin):
    """Plugin class."""

    plugins.implements(plugins.IConfigurer)
    plugins.implements(IReport)

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
