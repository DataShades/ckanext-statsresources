from __future__ import absolute_import

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckanext.report.interfaces import IReport

import ckanext.statsresources.views as views
from . import reports


class StatsresourcesPlugin(plugins.SingletonPlugin):
    """Plugin class."""

    plugins.implements(plugins.IConfigurer)
    plugins.implements(IReport)
    # plugins.implements(plugins.IBlueprint)

    # IBlueprint
    # def get_blueprint(self):
        # return views.get_blueprints()

    # IConfigurer

    def update_config(self, config_):
        """Update instance config."""
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("fanstatic", "statsresources")

    # IReport

    def register_reports(self):
        """Add custom reports."""
        return reports.stats_reports_info
