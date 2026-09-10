from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from .project_hours_report import build_project_hours_report
from .project_hours_excel import export_project_hours_excel
from .serializers import ProjectHoursReportSerializer
from .pagination import ReportPagination


class ReportViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = ReportPagination

    @action(
        detail=False,
        methods=['get'],
        url_path='project-hours',
    )
    def project_hours(self, request):
        serializer = ProjectHoursReportSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        report = build_project_hours_report(
            start_date=data['start_date'],
            end_date=data['end_date'],
        )

        export = request.query_params.get(
            'export',
            'json',
        )

        if export == 'excel':
            return export_project_hours_excel(
                report=report,
                start_date=data['start_date'],
                end_date=data['end_date'],
            )

        page = self.paginate_queryset(report)

        return self.get_paginated_response(page)
