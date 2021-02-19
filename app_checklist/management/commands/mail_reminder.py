import datetime

import requests
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from app_checklist.models import CheckListDone
from checklistmgr import settings


class Command(BaseCommand):
    """
    Send mail to managers that chaecklist valid_date expire in 30 days
    """
    help = 'Send mail reminder for expired checklists'

    def __init__(self):
        self.nb_days = 30

    def add_arguments(self, parser):
        """
        No args
        """
        # parser.add_argument('-w', '--wishes', action='store_true', help='just to add new wishes in database')
        ...

    def handle(self, *args, **kwargs):
        """
            Retrieve Checklists with valide_date = today + self.nb_days
            if email 1 or 2 --> Send mail in the manager's language
        """
        # wishes = kwargs['wishes']
        time = timezone.now().strftime('%X')
        print("mail_reminder started at %s" % time)
        today = datetime.date.today()
        date_future = today + datetime.timedelta(days=self.nb_days)
        chkdones = CheckListDone.objects.filter(cld_date_valid=date_future)
        for chkdone in chkdones:
            list_email = []
            print(chkdone.cld_manager)
            if chkdone.cld_manager.mgr_email1:
                # print('email1 : ', chkdone.cld_manager.mgr_email1)
                list_email.append(chkdone.cld_manager.mgr_email1)
            if chkdone.cld_manager.mgr_email2:
                # print('email2 : ', chkdone.cld_manager.mgr_email2)
                list_email.append(chkdone.cld_manager.mgr_email2)
            if chkdone.cld_email:
                # print('email : ', chkdone.cld_email)
                list_email.append(chkdone.cld_email)
            if list_email:
                language = chkdone.cld_manager.mgr_lang
                email_template_name = f"app_checklist/reminder_email-{language}.txt"
                society1 = str(chkdone.cld_company.address.street_number) + " " + \
                           str(chkdone.cld_company.address.street_type) + " " +\
                           str(chkdone.cld_company.address.address1)
                zipcity = str(chkdone.cld_company.address.zipcode) + " " + \
                          str(chkdone.cld_company.address.city) + " - " + \
                          str(chkdone.cld_company.address.country)
                c = {
                    "material": chkdone.cld_material.mat_designation,
                    'society': chkdone.cld_company.company_name,
                    'society1': society1,
                    'society2': chkdone.cld_company.address.address2,
                    'society3': zipcity,
                    'date_checklist': chkdone.created_date,
                    'date_valid': chkdone.cld_date_valid
                }
                subject = 'Reminder checklist'
                email = render_to_string(email_template_name, c)
                data = {"from": "Checklist Manager <webmaster@jm-hayons74.fr>",
                        "to": ','.join(list_email),
                        "subject": subject,
                        "text": email,
                        }
                mailgun_key = settings.MAILGUN_KEY
                print(list_email)
                try:
                    # send the mail
                    rc = requests.post(
                        "https://api.mailgun.net/v3/sandbox1f42285ff9e446fa9e90d34287cd8fee.mailgun.org/messages",
                        auth=("api", mailgun_key),
                        files=[],
                        data=data)
                    print(f"Retour send mail : {rc}")
                except:
                    pass
        print("mail_reminder at %s" % time)
