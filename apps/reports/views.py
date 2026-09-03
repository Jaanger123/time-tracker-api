from datetime import timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from .project_hours_report import build_project_hours_report
from .project_hours_excel import export_project_hours_excel
from .serializers import ProjectHoursReportSerializer


class ReportViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=['get'],
        url_path='project_hours',
    )
    def project_hours(self, request):
        serializer = ProjectHoursReportSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        report = build_project_hours_report(
            country_id=data['country_id'],
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

        return Response(report)
