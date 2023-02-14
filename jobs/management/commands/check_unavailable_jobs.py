import os
import json
from selenium.webdriver.chrome.options import Options
from django.core.management.base import BaseCommand
from django.conf import settings
from selenium.webdriver.support import expected_conditions as EC
import datetime
from django.utils import timezone
from jobs.models import Jobs, JobsStats
from jobs.utility import *


def startup():
    print(
        f"---------------------Update Unavailable Jobs Command Started {timezone.datetime.now()}----------------------\n")

    try:
        logging_file = open('logging/unavailable_jobs_update/start_up_end/daily_startup_and_close.txt', mode='a')
    except:
        path = str(settings.BASE_DIR) + '/logging/unavailable_jobs_update/start_up_end'
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)
            print(f"The new directory is created!: {path}")

        logging_file = open('logging/unavailable_jobs_update/start_up_end/daily_startup_and_close.txt', mode='a')

    logging_file.write(
        f"---------------------Update Unavailable Jobs Command Started {timezone.datetime.now()}----------------------")
    logging_file.close()

    jobs = Jobs.objects.filter(date__lt=timezone.now().date()-datetime.timedelta(days=5), available=True)
    driver = get_driver_with_vpn()

    try:
        logging_file = open(
            f'logging/unavailable_jobs_update/jobs_status/{timezone.datetime.today().date()}.txt',
            mode='a')
    except:
        path = str(settings.BASE_DIR) + '/logging/unavailable_jobs_update/jobs_status'
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)
            print(f"The new directory is created!: {path}")

        logging_file = open(
            f'logging/unavailable_jobs_update/jobs_status/{timezone.datetime.today().date()}.txt',
            mode='a')

    for job in jobs:
        try:
            driver.get(job.job_url)
            time.sleep(random.randint(1, 3))
            job_url = job.job_url

            if job_url[-1] != '/':
                job_url += '/'

            if driver.current_url != job.job_url:
                print(f"Job is no longer available job url: {job.job_url} and job id: {job.job_id}")

                job.available = False
                job.unavailable_date = timezone.now()
                job.save()

                logging_file.write(
                    f"Job is no longer available job url: {job.job_url} and job id: {job.job_id} \n")
            else:
                print(f"Job is still available job url: {job.job_url} and job id: {job.job_id}")

                logging_file.write(
                    f"Job is still available job url: {job.job_url} and job id: {job.job_id} \n")

        except:
            print(f"There is error in job url: {job.job_url} and job id: {job.job_id}")

            logging_file.write(
                f"There is error in job url: {job.job_url} and job id: {job.job_id} \n")

    logging_file.close()

    new_jobs_status = JobsStats.objects.filter(date__gt=timezone.datetime.today()).first()

    if not new_jobs_status:
        new_jobs_status = JobsStats()

    new_jobs_status.total_available = Jobs.objects.filter(available=True).count()
    new_jobs_status.total_unavailable = Jobs.objects.filter(available=False).count()
    new_jobs_status.save()

    print(f"---------------------Update Unavailable Jobs Command Ended {timezone.datetime.now()}----------------------")

    logging_file = open('logging/unavailable_jobs_update/start_up_end/daily_startup_and_close.txt', mode='a')
    logging_file.write(
        f"---------------------Update Unavailable Jobs Command Ended {timezone.datetime.now()}----------------------\n")
    logging_file.close()

    sleep_time = random.randint(50400, 82800)
    print(f'Waiting for {sleep_time % (24 * 3600)}')
    time.sleep(sleep_time)
    startup()


class Command(BaseCommand):
    def handle(self, *args, **options):
        startup()
