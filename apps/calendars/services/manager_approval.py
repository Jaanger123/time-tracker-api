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
            'task',
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
            'total_hours': 0,
            'approved_hours': 0,
            'projects': defaultdict(
                lambda: {
                    'project': None,
                    'project_code': None,
                    'total_hours': 0,
                    'approved_hours': 0,
                    'entries': [],
                }
            ),
        }
    )

    for entry in queryset:
        user_data = users[entry.user_id]
        user_data['user'] = entry.user

        user_data['total_hours'] += entry.hours

        if entry.is_approved:
            user_data['approved_hours'] += entry.hours

        project_data = user_data['projects'][
            entry.project_code_id
        ]

        project_data['project'] = entry.project_code.project
        project_data['project_code'] = entry.project_code

        project_data['total_hours'] += entry.hours

        if entry.is_approved:
            project_data['approved_hours'] += entry.hours

        project_data['entries'].append({
            'id': entry.id,
            'date': entry.date,
            'hours': entry.hours,
            'is_approved': entry.is_approved,
            'task': entry.task.name,
            'description': entry.description,
        })

    result = []

    for user_data in users.values():
        user = user_data['user']

        user_total_hours = user_data['total_hours']
        user_approved_hours = user_data['approved_hours']

        projects = []

        for project_data in user_data['projects'].values():
            project = project_data['project']
            project_code = project_data['project_code']

            total_hours = project_data['total_hours']
            approved_hours = project_data['approved_hours']

            projects.append({
                'project_id': project.id,
                'project_code': project_code.code,
                'approved_hours': approved_hours,
                'total_hours': total_hours,
                'entries': project_data['entries'],
            })

        result.append({
            'user_id': user.id,
            'full_name': f'{user.last_name} {user.first_name}',
            'email': user.email,
            'approved_hours': user_approved_hours,
            'total_hours': user_total_hours,
            'projects': projects,
        })

    return result