import datetime
import os
import random
import time

import spacy
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from jobs.models import Jobs
from skills.models import Skills


def startup():
    print(
        f"---------------------Update Skills Jobs Command Started {timezone.datetime.now()}----------------------\n")

    try:
        logging_file = open('logging/skills/start_up_end/daily_startup_and_close.txt', mode='a')
    except:
        path = str(settings.BASE_DIR) + '/logging/skills/start_up_end'
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)
            print(f"The new directory is created!: {path}")

        logging_file = open('logging/skills/start_up_end/daily_startup_and_close.txt', mode='a')

    logging_file.write(
        f"---------------------Update Unavailable Jobs Command Started {timezone.datetime.now()}----------------------")
    logging_file.close()
    jobs = Jobs.objects.filter(available=True)

    try:
        logging_file = open(
            f'logging/skills/skills_status/{timezone.datetime.today().date()}.txt',
            mode='a')
    except:
        path = str(settings.BASE_DIR) + '/logging/skills/skills_status'
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)
            print(f"The new directory is created!: {path}")

        logging_file = open(
            f'logging/skills/skills_status/{timezone.datetime.today().date()}.txt',
            mode='a')
    all_skills = Skills.objects.all()
    nlp = spacy.load("en_core_web_sm")

    for job in jobs:
        try:
            skills_list = []
            for skill in all_skills:
                skill_name = skill.name.lower()

                if skill_name in [chunk.text.lower() for chunk in nlp(job.title)] or skill_name in [chunk.text.lower()
                                                                                                    for chunk in
                                                                                                    nlp(job.post)]:
                    job.required_skills.add(skill)
                    skills_list.append(skill.name)

            print(f"update job with job_id: {job.job_id} with skills: {skills_list} ")
            logging_file.write(
                f"update job with job_id: {job.job_id} with skills: {skills_list} \n")
        except:
            print(f"There is error in adding skills job url: {job.job_url} and job id: {job.job_id}")

            logging_file.write(
                f"There is error in adding skills job url: {job.job_url} and job id: {job.job_id} \n")

    logging_file.close()

    print(f"---------------------Update Skills Jobs Command Ended {timezone.datetime.now()}----------------------")

    logging_file = open('logging/skills/start_up_end/daily_startup_and_close.txt', mode='a')
    logging_file.write(
        f"---------------------Update Skills Unavailable Jobs Command Ended {timezone.datetime.now()}----------------------\n")
    logging_file.close()

    sleep_time = random.randint(50400, 82800)
    print(f'Waiting for {sleep_time % (24 * 3600)}')
    time.sleep(sleep_time)
    startup()


class Command(BaseCommand):
    def handle(self, *args, **options):
        startup()

