from rest_framework import serializers


class ProjectHoursReportSerializer(serializers.Serializer):
    country_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, attrs):
        start_date = attrs['start_date']
        end_date = attrs['end_date']

        if start_date > end_date:
            raise serializers.ValidationError(
                '\'start_date\' cannot be greater than \'end_date\'.'
            )

        if (
            start_date.year != end_date.year
            or start_date.month != end_date.month
        ):
            raise serializers.ValidationError(
                'Report period must be within one month.'
            )

        return attrs
