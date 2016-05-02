from ckan import model
from ckan.lib.helpers import OrderedDict
from ckanext.report import lib
from ckan.lib.helpers import (
    url_for,
    Page
)
from ckanext.statsresources.helpers import get_org_title

OD = OrderedDict((
    ('organization', None),
    ('include_sub_organizations', False),
    ('include_private', False),
    ('include_draft', False),
))


def dataset_creation(organization=OD['organization'],
                     include_sub_organizations=OD['include_sub_organizations'],
                     include_private=OD['include_private'],
                     include_draft=OD['include_draft'],
                     page=1):
    """Produce a report with basic dataset info."""
    selectable_states = set(['active'])
    if include_draft:
        selectable_states.add('draft')

    query = model.Session.query(model.Package)\
        .filter(model.Package.type == 'dataset',
                model.Package.state.in_(selectable_states))
    if not include_private:
        query = query.filter(model.Package.private.is_(False))
    if organization:
        query = lib.filter_by_organizations(
            query, organization, include_sub_organizations)

    return {
        'table': [
            OrderedDict((
                ('title', pkg.title),
                ('url', url_for(controller='package', action='read', id=pkg.id, qualified=True)),
                ('owner', get_org_title(pkg)),
                ('created_at', pkg.metadata_created.isoformat()),
            )) for pkg in query.all()
        ],
        'a': query.count()
    }


def dataset_creation_combinations():
    """Return option combinations."""
    for organization in lib.all_organizations(include_none=True):
        for include_sub_organizations in (False, True):
            for include_private in (False, True):
                yield {
                    'organization': organization,
                    'include_sub_organizations': include_sub_organizations,
                    'include_private': include_private
                }


stats_reports_info = [
    {
        'name': 'dataset_creation',
        'title': 'Dataset creation',
        'description': 'Datasets with their generic information.',
        'option_defaults': OD,
        'option_combinations': dataset_creation_combinations,
        'generate': dataset_creation,
        'template': 'report/dataset-creation.html',
    },
]
