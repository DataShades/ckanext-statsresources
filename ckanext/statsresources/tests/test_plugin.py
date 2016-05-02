"""Tests for plugin.py."""
from ckan.tests.helpers import FunctionalTestBase
from ckanext.report.model import init_tables as init_report_tables
from pylons import config
from routes import url_for
from sqlalchemy import exc as sa_exc
import ckan.tests.factories as factories
import ckanext.statsresources.plugin as plugin
import csv
import json
import nose.tools as nt
import StringIO
import warnings

warnings.catch_warnings()
warnings.simplefilter("ignore", category=sa_exc.SAWarning)

DC_REPORT = 'dataset_creation'


class TestStatsReports(FunctionalTestBase):
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
        super(TestStatsReports, self).setup()
        init_report_tables()

    def test_always_true(self):
        """Everytime pass."""
        nt.assert_true(True, "Can't fail")

    def test_plugin_main(self):
        """Base test."""
        p = plugin.StatsresourcesPlugin()
        reports = p.register_reports()
        for report in reports:
            report_keys = set([
                'option_defaults', 'option_combinations', 'description',
                'template', 'generate', 'name', 'title'])
            nt.assert_equal(set(report.keys()) ^ report_keys, set(), 'Incorrect report keys')

    def test_data_creation_report_before_and_after_refresh(self):
        """Test report regeneration."""
        app = self._get_test_app()
        dr = self._get_dr(app, DC_REPORT)

        report1 = self._get_report(app, dr, True)
        factories.Dataset()
        report2 = self._get_report(app, dr)
        nt.assert_equal(report1[-1], report2[-1])

        report3 = self._get_report(app, dr, True)
        nt.assert_not_equal(report1[-1], report3[-1])

    def test_data_creation_private_option(self):
        """Test whether result differs for include_private."""
        app = self._get_test_app()
        dr = self._get_dr(app, DC_REPORT)

        org = factories.Organization()
        factories.Dataset(owner_org=org['id'])
        factories.Dataset(owner_org=org['id'])
        factories.Dataset(owner_org=org['id'], private=True)

        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 2)

        dr['option_defaults']['include_private'] = True
        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 3)

    def test_data_creation_draft_option(self):
        """Test whether result differs for include_draft."""
        app = self._get_test_app()
        dr = self._get_dr(app, DC_REPORT)

        org = factories.Organization()
        factories.Dataset(owner_org=org['id'])
        factories.Dataset(owner_org=org['id'])
        factories.Dataset(owner_org=org['id'], state='draft')

        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 2)

        dr['option_defaults']['include_draft'] = True
        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 3)

    def test_data_creation_draft_and_private_option(self):
        """Test whether result differs for include_draft and include_private."""
        app = self._get_test_app()
        dr = self._get_dr(app, DC_REPORT)

        org = factories.Organization()
        factories.Dataset(owner_org=org['id'])
        factories.Dataset(owner_org=org['id'])
        factories.Dataset(owner_org=org['id'], state='draft')
        factories.Dataset(owner_org=org['id'], state='draft')
        factories.Dataset(owner_org=org['id'], private=True)
        factories.Dataset(owner_org=org['id'], private=True)
        factories.Dataset(owner_org=org['id'], private=True)
        factories.Dataset(owner_org=org['id'], state='draft', private=True)
        factories.Dataset(owner_org=org['id'], state='draft', private=True)

        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 2)

        o = dr['option_defaults']
        o['include_draft'], o['include_private'] = True, False
        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 4)

        o['include_draft'], o['include_private'] = False, True
        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 5)

        o['include_draft'], o['include_private'] = True, True
        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 9)

    def test_data_creation_different_organizations(self):
        """Test whether result differs for different organizations."""
        app = self._get_test_app()
        dr = self._get_dr(app, DC_REPORT)
        o = dr['option_defaults']

        org1 = factories.Organization()
        org2 = factories.Organization()
        factories.Dataset()
        factories.Dataset()
        factories.Dataset()
        factories.Dataset()
        factories.Dataset(owner_org=org1['id'])
        factories.Dataset(owner_org=org1['id'])
        factories.Dataset(owner_org=org2['id'])
        factories.Dataset(owner_org=org2['id'])
        factories.Dataset(owner_org=org2['id'])
        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 9)

        o['organization'] = org1['name']
        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 2)
        o['organization'] = org2['name']
        nt.assert_equal(len(self._get_report(app, dr, True)[0]['table']), 3)

    def test_data_creation_json(self):
        """Test JSON report."""
        app = self._get_test_app()
        # dr = self._get_dr(app, DC_REPORT)
        admin = factories.Sysadmin()
        url = '/report/{0}'.format(DC_REPORT)
        kwpost = dict(
            headers={'Authorization': admin['apikey'].encode('ascii')}
        )

        d1 = factories.Dataset()
        d1_dict = dict(
            url=config.get('ckan.site_url') + url_for(controller='package', action='read', id=d1['id']),
            owner='',
            created_at=d1['metadata_created'],
            title=d1['title']
        )

        org = factories.Organization()
        d2 = factories.Dataset(owner_org=org['id'])
        d2_dict = dict(
            url=config.get('ckan.site_url') + url_for(controller='package', action='read', id=d2['id']),
            owner=org['title'],
            created_at=d2['metadata_created'],
            title=d2['title']
        )

        app.post(url, **kwpost)
        json_report = app.get(url + '?format=json').json['table']
        nt.assert_equal(len(json_report), 2)

        nt.assert_true(d1_dict in json_report)
        nt.assert_true(d2_dict in json_report)

        d3 = factories.Dataset()
        d3_dict = dict(
            url=config.get('ckan.site_url') + url_for(controller='package', action='read', id=d3['id']),
            owner='',
            created_at=d3['metadata_created'],
            title=d3['title']
        )
        nt.assert_false(d3_dict in json_report)

        app.post(url, **kwpost)
        json_report = app.get(url + '?format=json').json['table']
        nt.assert_equal(len(json_report), 3)

        nt.assert_true(d1_dict in json_report)
        nt.assert_true(d2_dict in json_report)
        nt.assert_true(d3_dict in json_report)

    def test_data_creation_csv(self):
        """Test CSV report."""
        app = self._get_test_app()
        # dr = self._get_dr(app, DC_REPORT)
        admin = factories.Sysadmin()
        url = '/report/{0}'.format(DC_REPORT)
        kwpost = dict(
            headers={'Authorization': admin['apikey'].encode('ascii')}
        )
        csv_file1 = StringIO.StringIO()
        fields = ['title', 'url', 'owner', 'created_at']
        csv_writer = csv.DictWriter(csv_file1, fields, quoting=csv.QUOTE_ALL)
        csv_writer.writerow(dict(zip(fields, fields)))

        d1 = factories.Dataset()
        csv_writer.writerow(dict(
            title=d1['title'],
            url=config.get('ckan.site_url') + url_for(
                controller='package', action='read', id=d1['id']),
            owner='',
            created_at=d1['metadata_created']
        ))

        org = factories.Organization()
        d2 = factories.Dataset(owner_org=org['id'])
        csv_writer.writerow(dict(
            title=d2['title'],
            url=config.get('ckan.site_url') + url_for(
                controller='package', action='read', id=d2['id']),
            owner=org['title'],
            created_at=d2['metadata_created']
        ))

        csv_file1.seek(0)
        required_report = csv_file1.read()

        app.post(url, **kwpost)
        csv_report = app.get(url + '?format=csv')

        nt.assert_equal(csv_report.body, required_report)

        d3 = factories.Dataset()
        csv_writer.writerow(dict(
            title=d3['title'],
            url=config.get('ckan.site_url') + url_for(
                controller='package', action='read', id=d3['id']),
            owner='',
            created_at=d3['metadata_created']
        ))

        app.post(url, **kwpost)
        csv_report = app.get(url + '?format=csv')
        nt.assert_not_equal(csv_report.body, required_report)

        csv_file1.seek(0)
        new_required_report = csv_file1.read()
        nt.assert_equal(csv_report.body, new_required_report)
