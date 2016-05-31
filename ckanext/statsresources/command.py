import pdb
from json import dumps
import ckan.plugins.toolkit as tk
from ckan.logic import get_action
import ckan.lib.helpers as h
from uuid import uuid3, NAMESPACE_DNS
from collections import namedtuple
import ckan.model as model
import requests
from StringIO import StringIO

Report = namedtuple('Report', 'name, format, package, title')


class StatsresourcesCommand(tk.CkanCommand):
    """
    Control statsresources.

    The available commands are:

        list     - Lists the reports

        generate - Generate/update all resources with reports

        generate {id[,id2]} - Generate particular report

    """

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = None
    min_args = 1

    def __init__(self, name):
        super(StatsresourcesCommand, self).__init__(name)

    def command(self):
        import logging

        self._load_config()
        self.log = logging.getLogger("ckan.lib.cli")
        config = self._get_config()
        self.__reports = [
            Report._make(x.split(':')) for x in
            config.get('statsresources.report_map', '').splitlines()
            if x.count(':') == 3
        ]
        self.sysadmin = model.Session.query(model.User).filter(
            model.User.sysadmin.is_(True)).first()

        self.rcu = h.url_for(
            controller='api',
            action='action',
            ver=3,
            logic_function='resource_create',
            qualified=True
        )
        self.rpu = h.url_for(
            controller='api',
            action='action',
            ver=3,
            logic_function='resource_patch',
            qualified=True
        )

        self.headers = {
            "X-CKAN-API-Key": "{0}".format(self.sysadmin.apikey)
        }

        # self.context = dict(
        #     model=model,
        #     ignore_auth=True)

        cmd = self.args[0]
        if cmd == 'list':
            self._list()
        elif cmd == 'generate':
            report_list = None
            if len(self.args) == 2:
                report_list = [s.strip() for s in self.args[1].split(',')]
                self.log.info("Running reports => %s", report_list)
            self._generate(report_list)
        else:
            self.parser.error('Command not recognized: %r' % cmd)

    def _list(self):
        print '*' * 80
        for i, report in enumerate(self.__reports, 1):
            print "#{0}. {1}".format(i, report)

    def _generate(self, report_list=None):
        if report_list:
            reports = filter(lambda r: r.name in report_list, self.__reports)
        else:
            reports = self.__reports

        for report in reports:
            pkg = model.Package.get(report.package)
            if not pkg:
                print "Unable to generate {0}: Dataset does not exists".format(
                    report)
            res_id = str(uuid3(NAMESPACE_DNS, report.package + report.format))
            resource = model.Resource.get(res_id)

            if resource and not resource.is_active():
                resource.purge()
                model.Session.commit()
                print "ERROR: Resource <{0.id}> in [{0.state}] state. Unable to generate {1}".format(
                    resource, report)
            if not resource:
                self._create_resource({
                    'package_id': report.package,
                    'id': res_id,
                    'name': report.title,
                    # 'name': '{0.format} Statistics({0.name})'.format(report),
                    'format': report.format,
                    'url': 'temporary_url'
                }, {'file': StringIO()})
            kwargs = {}
            try:
                op = self._get_config().get(
                    'statsresources.{0}.options'.format(report.name))
                if op:
                    kwargs = dict([
                        l.split(':')
                        for l in op.split()
                    ])
            except Exception:
                pass
            content = self._get_report_content(report, kwargs)

            get_file = StringIO(content)
            get_file.name = 'report.{0}'.format(report.format)

            self._upload_report({'id': res_id, 'name': report.title}, [('upload', get_file)])
            print "{0} generated".format(report)

    def _create_resource(self, data, files):
        requests.post(self.rcu, headers=self.headers, data=data, files=files)

    def _get_report_content(self, report, kwargs):
        url = self._get_report_url(report.name, report.format, kwargs)
        resp = requests.get(url, headers=self.headers)
        if report.format not in resp.headers['content-type']:
            print "{0.name}: Content-type from {1} does not contains report format.".format(report, url)
        return resp.content

    def _get_report_url(self, name, format, kwargs):
        return h.url_for('report', report_name=name, qualified=True, format=format, **kwargs)

    def _upload_report(self, data, files):
        requests.post(self.rpu, headers=self.headers, data=data, files=files)
