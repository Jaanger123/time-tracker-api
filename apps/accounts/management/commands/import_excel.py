import pandas as pd
from django.core.management.base import BaseCommand
from apps.accounts.models import Country, User
from apps.calendars.models import CountrySettings
import datetime

import uuid

from services.email_service import send_activation_email
from apps.projects.models import ProjectCode, Project
import re

class Command(BaseCommand):
    help = "Import data from Excel"

    def handle(self, *args, **kwargs):
        # email_list = [
        #     'kanykey.yussupova@mazars.kz',
        #     'aristarkh.saliev@mazars.kz',
        #     'nikita.boiko@mazars.kz',
        #     'samat.azharbayev@mazars.kz',
        #     'ozodbek.mahamatnazarov@mazars.uz',
        #     'anel.orynbayeva@mazars.kz',
        #     'aigerim.rysbekova@mazars.kg',
        #     'sezim.dubanaeva@mazars.kg',
        #     'ilyas.sherbekov@mazars.kg',
        #     'ariet.kozubekova@mazars.kg',
        #     'asadbek.niyozov@mazars.uz',
        #     'sadirbek.abdukhalilov@mazars.uz',
        #     'madina.igamberdiyeva@mazars.uz',
        #     'amaliya.isakova@mazars.uz',
        #     'ertay.esenbekov@mazars.kg',
        #     'emirbek.akimzhanov@mazars.kg',
        #     'jaanger.barakanov@mazars.kg',
        #     'turgut.dzhakeshev@mazars.kg',
        #     'dodojon.khojiev@mazars.kg'
        # ]
        # print(uuid.uuid4())
        # users = User.objects.filter(email__in=email_list)
        project = Project.objects.filter(id=447)[0]

        queryset = ProjectCode.objects.filter(
            project=project
        )
        print(queryset)
        # users = User.objects.all()

        # for user in users:
        #     if user.activation_code == None:
        #         continue
        #     send_activation_email(user)
        #     print(user.activation_code)
            # print(type(user.activation_code))
        # send_activation_email
        # df = pd.read_excel('time_tracker_tables.xlsx', sheet_name='projects_projectcode')
        # User.objects.all().delete()
        # print(df['date_joined'])
        # df = df.fillna('')
        # send_activation_email(User.objects.filter(email='jbarakanov@gmail.com').first())
        # for user in users:
        #     send_activation_email(user)
            # CountrySettings.objects.create(country=country)
        # for _, row in df.iterrows():
            # ProjectCode.objects.create(
            #     id=row['id'],
            #     code=row['code'],
            #     project_id=row['project_id'],
                # entity=row['entity'],
                # is_code_recurring=row['is_code_recurring'],
                # is_chargeable=row['is_chargeable'],
                # country_id=row['country_id'],
                # department_id=row['department_id'],
                # manager_id=row['manager_id'],
                # status_id=row['status_id'],
                # service_line_id=row['service_line_id'],
                # task_type_id=row['task_type_id'],
                # client_id=row['client_id'],
                # service_type_id=row['service_type_id'],
                # agreement_date=datetime.datetime.now()
            # )

        # Project.objects.create(
        #     name='ADM Jizzakh LLC',
        #     group='',
        #     personal_number='307057209',
        #     bvd='UZ307057209',
        #     sector_id=22,
        #     client_code='ADM-JIZZAKH',
        #     pie_id='',
        #     country_id=3
        # )

        self.stdout.write(self.style.SUCCESS("Import completed"))