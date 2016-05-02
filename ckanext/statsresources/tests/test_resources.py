"""Tests for plugin.py."""
from ckanext.report.model import init_tables as init_report_tables
import nose.tools as nt
import json
import sys
from ckan import model
from ckan.tests.helpers import FunctionalTestBase, change_config, _get_test_app
import ckan.tests.factories as factories
from routes import url_for
import warnings
from sqlalchemy import exc as sa_exc

from ckanext.statsresources.command import StatsresourcesCommand

warnings.catch_warnings()
warnings.simplefilter("ignore", category=sa_exc.SAWarning)

DC_REPORT = 'dataset_creation'


class TestStatsResources(FunctionalTestBase):
    """Main test class."""

    def _refresh_report(self, dr):
        admin = factories.Sysadmin()
        self._get_test_app().post(
            url='/api/action/report_refresh',
            params=json.dumps({
                'id': dr['name'],
                'options': dr['option_defaults']}),
            headers={'Authorization': admin['apikey'].encode('ascii')}
        )

    def _get_dr(self, app, report):
        return app.get('/api/action/report_show', params={
            'id': report}).json['result']

    def _get_report(self, app, dr, refresh=False):
        """Simple report getter."""
        refresh and self._refresh_report(dr)
        return app.post('/api/action/report_data_get', params=json.dumps({
            'id': dr['name'],
            'options': dr['option_defaults']
        })).json['result']

    def setup(self):
        """Run before each test."""
        super(TestStatsResources, self).setup()
        init_report_tables()

        self.main_page = url_for('reports')
        self.dc_page = url_for('report', report_name=DC_REPORT)
        self.base_dataset = factories.Dataset()

        self.cmd = StatsresourcesCommand('statsresources')

        class Options:
            config = filter(
                lambda x: x.startswith('--with-pylons'), sys.argv).pop()[14:]

        self.cmd.options = Options

        self.cmd._get_report_content = self._get_report_content
        self.cmd._create_resource = self._create_resource
        self.cmd._upload_report = self._upload_report

    def _get_report_content(self, report):
        app = _get_test_app()
        return app.get(url_for('report', report_name=report.name, format=report.format))

    def _create_resource(self, data, files):
        factories.Resource(**data)

    def _upload_report(self, data, files):
        app = _get_test_app()
        s = factories.Sysadmin()

        app.post(
            self.cmd.rpu[self.cmd.rpu.find('/api'):],
            params=data,
            headers={
                'Authorization': str(s['apikey']),
            },
            upload_files=[(files[0][0], 'x.csv', files[0][1].read())])

    def run_command(self, command):
        self.cmd.args = [command]
        self.cmd.command()

    def test_always_true(self):
        """Everytime pass."""
        nt.assert_true(True, "Can't fail")

    def test_not_strict_access(self):
        """Report page visible without strict access."""
        app = _get_test_app()
        nt.assert_equal(app.get(self.main_page).status_int, 200)
        nt.assert_equal(app.get(self.dc_page).status_int, 200)

    @change_config('reports.strict_access', 'true')
    def test_strict_access(self):
        """Report page not available with strict access."""
        app = _get_test_app()

        nt.assert_not_equal(app.get(self.main_page).status_int, 200)
        nt.assert_not_equal(app.get(self.dc_page).status_int, 200)

    @change_config('reports.strict_access', 'true')
    def test_strict_access_for_admin(self):
        """Report page are available for admin even with strict access."""
        app = _get_test_app()
        s = factories.Sysadmin()
        nt.assert_equal(app.get(self.main_page, headers={
            'Authorization': str(s['apikey'])
        }).status_int, 200)
        nt.assert_equal(app.get(self.dc_page, headers={
            'Authorization': str(s['apikey'])
        }).status_int, 200)

    def test_report_resources(self):
        """Test report generation."""
        d1 = factories.Dataset(name='first_package')
        factories.Dataset()

        self.run_command('generate')

        pkg = model.Package.get(d1['id'])
        nt.assert_equal(len(pkg.resources), 2)
        formats = [r.format.lower() for r in pkg.resources]
        nt.assert_true('json' in formats)
        nt.assert_true('csv' in formats)
