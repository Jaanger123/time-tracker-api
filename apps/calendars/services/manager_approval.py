from collections import defaultdict

from apps.calendars.utils import filter_manager_approval_by_params
from apps.calendars.models import TimeEntry


def get_manager_approval_data(request):
    queryset = (
        TimeEntry.objects
        .filter(
            project_code__isnull=False,
            project_code__project__manager=request.user,
        )
        .select_related(
            'user',
            'user__country',
            'user__department',
            'user__position',
            'user__grade',
            'project_code',
            'project_code__project',
        )
        .order_by(
            'user__email',
            'project_code__code',
            'date',
            'id',
        )
    )

    queryset = filter_manager_approval_by_params(request, queryset)

    users = defaultdict(
        lambda: {
            'user': None,
            'projects': defaultdict(
                lambda: {
                    'project': None,
                    'project_code': None,
                    'entries': [],
                }
            ),
        }
    )

    for entry in queryset:
        user_data = users[entry.user_id]
        user_data['user'] = entry.user

        project_data = user_data['projects'][
            entry.project_code_id
        ]

        project_data['project'] = entry.project_code.project
        project_data['project_code'] = entry.project_code

        project_data['entries'].append({
            'id': entry.id,
            'date': entry.date,
            'hours': entry.hours,
            'is_approved': entry.is_approved,
        })

    result = []

    for user_data in users.values():
        user = user_data['user']

        projects = []

        for project_data in user_data['projects'].values():
            project = project_data['project']
            project_code = project_data['project_code']

            projects.append({
                'project_id': project.id,
                'project_code': project_code.code,
                'entries': project_data['entries'],
            })

        result.append({
            'user_id': user.id,
            'full_name': f'{user.last_name} {user.first_name}',
            'email': user.email,
            'projects': projects,
        })

    return result