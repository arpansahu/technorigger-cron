import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from selenium.webdriver.support import expected_conditions as EC
import datetime
import traceback as tb
import re

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By

from jobs.utility import *

from companies.models import Company
from locations.models import Locations
from jobs.models import Jobs, JobsStats
from skills.models import Skills

import spacy

all_skills = Skills.objects.all()
nlp = spacy.load("en_core_web_sm")


def add_skill(job):
    skills_list = []
    for skill in all_skills:
        skill_name = skill.name.lower()

        if skill_name in [chunk.text.lower() for chunk in nlp(job.title)] or skill_name in [chunk.text.lower()
                                                                                            for chunk in
                                                                                            nlp(job.post)]:
            job.required_skills.add(skill)
            skills_list.append(skill.name)

    print(f"update job with job_id: {job.job_id} with skills: {skills_list} ")


def browserstack(base_url, company_obj):
    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/start_up_end'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    logging_file = open(f'logging/{company_obj.name.lower()}/start_up_end/{company_obj.name.lower()}_logging.txt',
                        mode='a')
    logging_file.write(
        f"---------------------Update {company_obj.name} Jobs Started {timezone.datetime.now()}----------------------\n\n")
    logging_file.close()
    print(
        f"---------------------Update {company_obj.name} Jobs Started {timezone.datetime.now()}----------------------\n\n")

    initial_time = timezone.datetime.now()
    # connect_to_vpn()

    driver = get_driver_with_vpn()
    driver.get(base_url)
    locations = driver.find_elements(By.CLASS_NAME, 'location-card-wrapper')
    job_objects = {}
    print('started scraping')
    for location in locations:
        locations_and_position = str(location.text).split('\n')
        remo = '.cls-1{fill:none;}.cls-2{clip-path:url(#clip-path);}.cls-3{fill:#bcbcbb;}.cls-4{' \
               'fill:#fff;}Location_New York'

        if remo in locations_and_position:
            locations_and_position.remove(remo)

        location = None
        for index in range(0, len(locations_and_position), 2):
            city_country = locations_and_position[index]

            try:
                city = city_country.split(',')[0]

                if city == 'Mumbai':
                    location = Locations.objects.get(city=city)
                    location_url = 'mumbai-india'
                if city == 'San Francisco':
                    location = Locations.objects.get(city=city, country='United States')
                    location_url = 'san-francisco-united-states'
                if city == 'Dublin':
                    location = Locations.objects.get(city=city, country='Ireland')
                    location_url = 'dublin-ireland'
                if city == 'US Remote':
                    city = 'Remote'
                    location = Locations.objects.get(city=city, country='United States')
                    location_url = 'us-remote'
                if city == 'New York':
                    location = Locations.objects.get(city=city)
                    location_url = 'new-york'
                if city == 'Atlanta':
                    location = Locations.objects.get(city=city)
                    location_url = 'atlanta'

                print('----------', city, location_url, '-----------')
                driver.get(base_url + '/' + location_url)
                category_index = 1
                category = driver.find_elements(By.XPATH, '//*[@id="bd-careers"]/section/div[2]/div[2]/div/div/div[' +
                                                str(category_index) + ']')
                while category:
                    print("Category Name: {}".format(category[0].text))
                    category_name = category[0].text
                    driver.get(base_url + '/' + location_url + '#' + category[0].text.lower())
                    driver.refresh()
                    job_index = 1
                    link = driver.find_elements(By.XPATH, '//*[@id="bd-careers"]/section/div[2]/div[3]/div/div['
                                                + str(category_index) + ']/ul/li[' + str(job_index)
                                                + ']/a/div/div[2]/button ')
                    job_title = driver.find_elements(By.XPATH, '//*[@id="bd-careers"]/section/div[2]/div[3]/div/div['
                                                     + str(category_index) + ']/ul/li[' + str(job_index) +
                                                     ']/a/div/div[''1]/div')
                    while link:
                        job = job_title[0].text
                        job_id = link[0].get_attribute('data-workable-id')
                        job_url = 'https://apply.workable.com/browserstack-2/j/' + job_id
                        print(job, job_id, job_url)
                        if job_id != '':  # append job_id iff job_id not None
                            job_objects[job_id] = {
                                'location': location,
                                'job_url': job_url,
                                'job_id': job_id,
                                'job_title': job,
                                'job_category': category_name
                            }
                        print(
                            f'job_id: {job_id} job_url: {job_url} location: {location} job_title: {job_title} job_category: {category_name} ')
                        job_index += 1
                        link = driver.find_elements(By.XPATH, '//*[@id="bd-careers"]/section/div[2]/div[3]/div/div['
                                                    + str(category_index) + ']/ul/li[' + str(job_index)
                                                    + ']/a/div/div[2]/button ')
                        job_title = driver.find_elements(By.XPATH,
                                                         '//*[@id="bd-careers"]/section/div[2]/div[3]/div/div['
                                                         + str(category_index) + ']/ul/li[' + str(job_index) +
                                                         ']/a/div/div[''1]/div')
                    time.sleep(2)
                    category_index += 1
                    category = driver.find_elements(By.XPATH,
                                                    '//*[@id="bd-careers"]/section/div[2]/div[2]/div/div/div[' +
                                                    str(category_index) + ']')

            except Exception as error:
                print("error occurred :{} ".format(error))
                print("trace:{}".format(tb.format_exc().replace("\n", " ")))

    json_dict = {}
    for keys in job_objects:
        obj = job_objects[keys]
        obj['location'] = [obj['location'].city, obj['location'].country]
        json_dict[keys] = obj

    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/daily_jobs'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    file_name = f'logging/{company_obj.name.lower()}/daily_jobs/{company_obj.name.lower()}_{str(timezone.datetime.today().date())}.json'

    with open(file_name, "w") as write_file:
        json.dump(json_dict, write_file)

    f = open(file_name, "r")
    data = json.loads(f.read())

    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/daily_jobs_info'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    daily_jobs_info_file = f'logging/{company_obj.name.lower()}/daily_jobs_info/{company_obj.name.lower()}_{str(timezone.datetime.today().date())}.txt'
    count = 1
    for keys in data:
        job = data[keys]
        print(f'----Job no : {count} and Job url: {job["job_url"]} ----', end='', sep='')
        logging_str = f'----{job["job_url"]} ----'

        if job['job_id'] and not Jobs.objects.filter(job_id=job['job_id'], company=company_obj):
            print('-new found job-', sep='', end='')
            logging_str += '-new found job-'

            # change  vpn
            # now_plus_5 = initial_time + datetime.timedelta(minutes=5)
            # if timezone.datetime.now() > now_plus_5:

            #     os.system("windscribe disconnect")
            #     vpn_choice_code = random.choice(codeList)
            #     os.system("windscribe connect " + vpn_choice_code)
            #
            #     initial_time = now_plus_5

            driver.get(job['job_url'])
            time.sleep(2)

            if driver.current_url == job['job_url'] + '/':
                div_len = len(driver.find_elements(By.XPATH, '//*[@id="app"]/div/div/div//main/div')) - 1
                post = ""
                div_count = 2

                while div_len:
                    div_obj = driver.find_elements(By.XPATH,
                                                   f'//*[@id="app"]/div/div/div/main/div[{div_count}]').__getitem__(0)
                    post += div_obj.text + '\n'
                    div_count += 1
                    div_len -= 1

                job_obj = Jobs(title=job['job_title'], category=job['job_category'], company=company_obj,
                               post=post,
                               job_id=job['job_id'], job_url=job['job_url'])

                job_obj.save()
                location_obj = Locations.objects.filter(city=job['location'][0], country=job['location'][1]).first()
                job_obj.location.add(location_obj.id)
                add_skill(job_obj)

                print('-Saved in database-')
                logging_str += '-Saved in database-'

            else:
                print('-Not Saved into database-')
                logging_str += '-Not Saved into database-'
        else:
            print('-already in database-', sep='', end='')
            logging_str += '- already in database-'

        logging_file = open(daily_jobs_info_file, mode='a')
        logging_file.write(logging_str)
        logging_file.close()

        count += 1

    # disconnect_to_vpn()

    logging_file = open(f'logging/{company_obj.name.lower()}/start_up_end/{company_obj.name.lower()}_logging.txt',
                        mode='a')
    logging_file.write(
        f"---------------------Update {company_obj.name} Jobs Ended {timezone.datetime.now()}----------------------\n\n")
    logging_file.close()
    f"---------------------Update {company_obj.name} Jobs Ended {timezone.datetime.now()}----------------------\n\n"
    driver.close()


def meta(base_url, company_obj):
    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/start_up_end'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    logging_file = open(f'logging/{company_obj.name.lower()}/start_up_end/{company_obj.name.lower()}_logging.txt',
                        mode='a')
    logging_file.write(
        f"---------------------Update {company_obj.name} Jobs Started {timezone.datetime.now()}----------------------\n\n")
    logging_file.close()
    print(
        f"---------------------Update {company_obj.name} Jobs Started {timezone.datetime.now()}----------------------\n\n")

    # connect to vpn
    # connect_to_vpn()
    # initial_time = timezone.datetime.now()

    driver = get_driver_with_vpn()
    driver.get(base_url)

    try:
        WebDriverWait(driver, 10).until(EC.url_to_be(base_url))
    except:
        print("page is taking so much time to load")

    # select count per page

    page_count = 1
    results_per_page = 100
    page_url = base_url + f'?page={page_count}&results_per_page={results_per_page}#search_result'

    page_loop_cond = True
    all_jobs_without_post = {}

    while page_loop_cond:

        # change  vpn
        # now_plus_5 = initial_time + datetime.timedelta(minutes=5)
        # if timezone.datetime.now() > now_plus_5:
        #     os.system("windscribe disconnect")
        #     vpn_choice_code = random.choice(codeList)
        #     os.system("windscribe connect " + vpn_choice_code)
        #
        #     initial_time = now_plus_5

        print(f"---------------------------pageno: {page_count} --------------------------------")
        driver.get(page_url)
        time.sleep(10)

        all_buttons = driver.find_elements(By.TAG_NAME, 'button')

        for button in all_buttons:
            if button.text == 'Accept All':
                button.click()

        for job_count_on_page in range(1, results_per_page + 1):
            try:
                job_url = driver.find_elements(By.XPATH, f'//*[@id="search_result"]/div[3]/a[{job_count_on_page}]')
                job_url = job_url[0].get_attribute('href')
            except:
                print('-----------------------job url not found ---------------------')
                continue

            try:
                job_id = job_url.split('/jobs/')[1][:-1]
            except:
                print('-----------------------job_id not found ---------------------')
                continue

            try:
                title = driver.find_elements(By.XPATH,
                                             f'//*[@id="search_result"]/div[3]/a[{job_count_on_page}]/div/div/div/div[1]')
                title = title[0].text
            except:
                print('-----------------------job title not found ---------------------')
                continue

            locations = []
            main_location = driver.find_elements(By.XPATH,
                                                 f'//*[@id="search_result"]/div[3]/a[{job_count_on_page}]/div/div/div/div['
                                                 f'3]/div[1]/div/div')
            try:
                main_location = main_location[0].text
                locations.append(main_location)
            except:
                print(f'error in main location-----------------{job_id} and {job_url}')
                locations.append('Invalid, Invalid')
                continue

            extra_locations_cond = len(driver.find_elements(By.XPATH,
                                                            f'//*[@id="search_result"]/div[3]/a[{job_count_on_page}]/div/div/div/div[3]/div[1]/div/div/div'))
            try:
                if extra_locations_cond:
                    extra_locations = driver.find_elements(By.XPATH,
                                                           f'/html/body/div[1]/div/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div/div/div[3]/a[{job_count_on_page}]/div/div/div/div[3]/div[1]/div/div/div')
                    extra_locations = extra_locations[0].get_attribute('data-tooltip-content')
                    extra_locations = extra_locations.split('\n')
                    for ex_loc in extra_locations:
                        locations.append(ex_loc)
            except:
                print(f'error in extra location-----------------{job_id} and {job_url}')


            category = driver.find_elements(By.XPATH,
                                            f'//*[@id="search_result"]/div[3]/a[{job_count_on_page}]/div/div/div/div['
                                            f'3]/div[2]/div[3]/div[2]/div/div')

            sub_category = driver.find_elements(By.XPATH,
                                                f'//*[@id="search_result"]/div[3]/a[{job_count_on_page}]/div/div/div/div[3]/div[2]/div[2]/div/div')
            sub_category = sub_category[0].text
            try:
                category = category[0].text
            except:
                print('----------------Category Not Found-------------------', job_url)
                category = sub_category

            if title == '' or len(locations) == 0 or category == '' or job_id == '' or job_id == '':
                print('---------------inside something is empty----------------------------')

            try:
                all_jobs_without_post[job_id] = {
                    'title': title,
                    'location': locations,
                    'category': category,
                    'job_url': job_url,
                    'job_id': job_id,
                    'subcategory': sub_category
                }

                print(f"pageno: {page_count} jobd no: {job_count_on_page}", all_jobs_without_post[job_id])
            except:
                continue

        len_of_next_prev_buttons = len(driver.find_elements(By.XPATH, '//*[@id="search_result"]/div[4]/div[2]/a'))

        if len_of_next_prev_buttons == 1 and page_count > 1:
            page_loop_cond = False
        # Increasing page count
        page_count += 1
        page_url = base_url + f'?page={page_count}&results_per_page={results_per_page}#search_result'

    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/daily_jobs'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    file_name = f'logging/{company_obj.name.lower()}/daily_jobs/{company_obj.name.lower()}_{str(timezone.datetime.today().date())}.json'
    with open(file_name, "w") as write_file:
        json.dump(all_jobs_without_post, write_file)

    f = open(file_name, "r")
    data = json.loads(f.read())

    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/daily_jobs_info'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    daily_jobs_info_file = f'logging/{company_obj.name.lower()}/daily_jobs_info/{company_obj.name.lower()}_{str(timezone.datetime.today().date())}.txt'

    count = 1
    for keys in data:
        logging_str = ''
        job = data[keys]
        job_locations_objects = []
        print(f'--------------job no: {count}------------{job["job_url"]}-------', sep='', end='')
        logging_str += f'--------------job no: {count}------------{job["job_url"]} -------'

        # if job['job_id'] == '426875042300078':
        if not Jobs.objects.filter(job_id=job['job_id'], company=company_obj) and len(job['location']):
            print(f'-have-', sep='', end='')
            logging_str += f'-have-'

            # Found Locations Objects from database
            for location in job['location']:

                city = location.split(',')[0].strip()

                # if city == 'Singapore':
                #     country = 'Singapore'
                # else:
                try:
                    country = location.split(',')[1].strip()
                except:
                    country = city
                # print(city, country)

                # Regex Filtering
                country = re.sub("[+]\d* more", ' ', country)
                country = country.strip()

                if country in ['SC', 'DC', 'MN', 'IL', 'ND', 'AS', 'CO', 'CA', 'UT', 'SD', 'IN', 'ID', 'UM', 'VI', 'NE',
                               'AZ', 'KY', 'WY', 'AK', 'NY', 'IA', 'NJ', 'KS', 'MO', 'OR', 'GA', 'MA', 'TX', 'WA', 'PR',
                               'MI', 'GU', 'NV', 'OK', 'NM', 'DE', 'OH', 'MT', 'PA', 'HI', 'CT', 'NC', 'RI', 'FL', 'VT',
                               'WI', 'MD', 'TN', 'NH', 'AL', 'AR', 'WV', 'MP', 'ME', 'VA', 'LA', 'MS', 'US']:
                    country = 'United States'

                elif country in ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'ON', 'PE', 'QC', 'SK', 'NT', 'NU', 'YT']:
                    country = 'Canada'
                elif country == 'UK':
                    country = 'United Kingdom'
                elif city == 'Bogotá':
                    city = 'Bogota'
                elif city == 'São Paulo':
                    city = 'Sao Paulo'
                elif city == 'Luleå':
                    city = 'Lulea'
                try:
                    try:
                        location_obj = Locations.objects.get(city=city, country=country)
                    except:
                        all_characters = ['2', '6', 'f', 'S', '1', 'u', 'R', 'B', 'N', 'D', 'U', 'x', 'G', 'K', 'e',
                                          ')', 'J', 'O', 'W', 'w', 'P', 'V', 'k', '(', 'M', 'i', 'r', '.', 'X', ',',
                                          '-', '`', 'H', "'", '/', 'v', 'd', 'o', 'b', 'C', 'l', 'Q', 'E', 'T', 'n',
                                          'q', 'A', 'h', '7', 'c', '4', 'L', 'a', '5', 'F', 'Z', 'z', 'Y', 'p', 'y',
                                          '9', 's', 'j', 'g', 't', '8', '0', ' ', '3', 'm', 'I']
                        loc_cond = True
                        for each_char in city:
                            if each_char not in all_characters:
                                loc_cond = False
                        if loc_cond:
                            location_obj = Locations.objects.get_or_create(city=city, country=country)
                            try:
                                for_iso_codes = Locations.objects.get(country=country)

                                location_obj.country_code_iso2 = for_iso_codes.country_code_iso2
                                location_obj.country_code_iso3 = for_iso_codes.country_code_iso3
                            except:
                                print(f'-Error in Iso Codes-')
                                logging_str += f'-Error in Iso Codes-'
                            location_obj.save()

                    job_locations_objects.append(location_obj)
                except:
                    print(f'-Error in locations-', sep='', end='')
                    logging_str += f'-Error in locations-'

            print(f'-Locations: {[location.id for location in job_locations_objects]}-', sep='', end='')
            logging_str += f'-Locations: {[location.id for location in job_locations_objects]}-'

            # change  vpn
            # now_plus_5 = initial_time + datetime.timedelta(minutes=2)
            # if timezone.datetime.now() > now_plus_5:
            #     re_connect_to_vpn()
            #     initial_time = now_plus_5

            driver.get(job['job_url'])
            # time.sleep(random.randint(1, 5))

            # Check Current Url to Check if current Job is Available or not
            if driver.current_url == job['job_url']:
                all_buttons = driver.find_elements(By.TAG_NAME, 'button')

                for button in all_buttons:
                    if button.text == 'Accept All':
                        button.click()

                # Extracting Post Data

                post = ''
                total_no_of_divs_in_a_post = len(driver.find_elements(By.XPATH,
                                                                      '//*[@id="careersContentContainer"]/div/div['
                                                                      '3]/div[2]/div/div/div[1]/div[1]/div'))

                try:
                    for div_count in range(1, total_no_of_divs_in_a_post + 1):
                        element = driver.find_elements(By.XPATH,
                                                       f'//*[@id="careersContentContainer"]/div/div[3]/div['
                                                       f'2]/div/div/div[1]/div[1]/div[{div_count}]')
                        text = element[0].text

                        if text == '':
                            continue
                        if div_count == 1:
                            post += text + '\n\n\n'
                        else:
                            first_line = text.split('\n')[0]

                            if first_line != 'Locations':
                                post += first_line + '\n\n'

                                text = text.replace(first_line + '\n', '')
                                post += text + '\n\n\n'
                except:
                    print(f'-Error In Post-', end='', sep='')
                    logging_str += f'-Error In Post-'

                new_job_obj = Jobs(title=data[keys]['title'], category=data[keys]['category'].split('+')[0],
                                   sub_category=data[keys]['subcategory'].split('+')[0], post=post,
                                   job_url=data[keys]['job_url'], job_id=data[keys]['job_id'], company=company_obj)
                new_job_obj.save()
                print(f'-saved into database-', end='', sep='')
                logging_str += f'-saved into database-'
                for loc in job_locations_objects:
                    new_job_obj.location.add(loc)
                add_skill(new_job_obj)
            else:
                print(f'-Not Saved into database-', sep='', end='')
                logging_str += f'-Not Saved into database-'
        else:
            if len(job['location']):
                print('-already in database-', sep='', end='')
                logging_str += '-already in database-'
            else:
                print('-not have location-', sep='', end='')
                logging_str += '-not have location-'
        count = count + 1
        print()
        logging_str += '\n'

        logging_file = open(daily_jobs_info_file, mode='a')
        logging_file.write(logging_str)
        logging_file.close()

        # disconnect_to_vpn()

    logging_file = open(f'logging/{company_obj.name.lower()}/start_up_end/{company_obj.name.lower()}_logging.txt',
                        mode='a')
    logging_file.write(
        f"---------------------Update {company_obj.name} Jobs Ended {timezone.datetime.now()}----------------------\n\n")
    logging_file.close()
    f"---------------------Update {company_obj.name} Jobs Ended {timezone.datetime.now()}----------------------\n\n"
    driver.close()


def walmart_global_tech_india(base_url, company_obj):
    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/start_up_end'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    logging_file = open(f'logging/{company_obj.name.lower()}/start_up_end/{company_obj.name.lower()}_logging.txt',
                        mode='a')
    logging_file.write(
        f"---------------------Update {company_obj.name} Jobs Started {timezone.datetime.now()}----------------------\n\n")
    logging_file.close()
    print(
        f"---------------------Update {company_obj.name} Jobs Started {timezone.datetime.now()}----------------------\n\n")

    driver = get_driver_with_vpn()
    driver.get(base_url)

    try:
        WebDriverWait(driver, 10).until(EC.url_to_be(base_url))
    except:
        print("page is taking so much time to load")

    # clicking on load button
    time.sleep(2)
    button = True
    while button:
        load_button = driver.find_elements(By.XPATH,
                                           '/html/body/segmentation-timeout/div[1]/div[3]/div[2]/div/div/div[1]/div[2]/div[2]/div[2]/button')
        if len(load_button):
            try:
                load_button[0].click()
            except:
                print('-------------------page has loaded-----------')
        No_result = driver.find_elements(By.CLASS_NAME, 'no-results')
        if len(No_result) > 1:
            button = False

    # taking div of jobs

    results_on_page = driver.find_elements(By.CLASS_NAME, 'result-section')
    lresults_on_page = len(results_on_page)
    print(lresults_on_page)
    all_jobs_without_post = {}
    for job_count_on_page in range(1, lresults_on_page + 1):

        try:

            title = driver.find_elements(By.XPATH,
                                         f'/html/body/segmentation-timeout/div[1]/div[3]/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/div[{job_count_on_page}]/div[1]/div[1]')
            title = title[0].text
        except:
            no_result = driver.find_elements(By.XPATH,
                                             f'/html/body/segmentation-timeout/div[1]/div[3]/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/div[{job_count_on_page}]/div[@class="no-results"]')
            print(len(no_result))
            if len(no_result):
                print("-----------------no result found-----------------")
                continue
            else:
                print('-----------------------job title not found ---------------------')
                continue

        try:
            location = driver.find_elements(By.XPATH,
                                            f'/html/body/segmentation-timeout/div[1]/div[3]/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/div[{job_count_on_page}]/div[1]/div[2]')
            location = location[0].text.split('|')[1].strip()
            print(location)

        except:
            print('-----------------------job location not found ---------------------')
            continue
        try:
            posted_date = driver.find_elements(By.XPATH,
                                               f'/html/body/segmentation-timeout/div[1]/div[3]/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/div[{job_count_on_page}]/div[1]/div[2]')

            posted_date = posted_date[0].text.split('|')[0].strip()

        except:
            print('-----------------------posted date not found ---------------------')
            continue

        try:
            job_url = driver.find_elements(By.XPATH,
                                           f'/html/body/segmentation-timeout/div[1]/div[3]/div[2]/div/div/div[1]/div[2]/div[2]/div[1]/div[{job_count_on_page}]/div[1]/div[1]/a')
            job_url = job_url[0].get_attribute('href')
            print(job_url)
        except:
            print('-----------------------job url not found ---------------------')
            continue

        try:
            job_id = job_url.split('-')[-1]

        except:
            print('-----------------------job_id not found ---------------------')
            continue

        if title == '' or len(location) == 0 or posted_date == '' or job_id == '' or job_url == '':
            print('---------------inside something is empty----------------------------')

        try:
            all_jobs_without_post[job_id] = {
                'title': title,
                'location': location,
                'posted_date': posted_date,
                'job_url': job_url,
                'job_id': job_id,
            }

            print(f" job no: {job_count_on_page}", all_jobs_without_post[job_id])
        except:
            continue

    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/daily_jobs'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    file_name = f'logging/{company_obj.name.lower()}/daily_jobs/{company_obj.name.lower()}_{str(timezone.datetime.today().date())}.json'
    with open(file_name, "w") as write_file:
        json.dump(all_jobs_without_post, write_file)

    f = open(file_name, "r")
    data = json.loads(f.read())

    path = str(settings.BASE_DIR) + f'/logging/{company_obj.name.lower()}/daily_jobs_info'
    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created!: {path}")

    daily_jobs_info_file = f'logging/{company_obj.name.lower()}/daily_jobs_info/{company_obj.name.lower()}_{str(timezone.datetime.today().date())}.txt'

    count = 1
    for keys in data:
        logging_str = ''
        job = data[keys]
        job_locations_objects = []
        print(f'--------------job no: {count}------------{job["job_url"]} -------', sep='', end='')
        logging_str += f'--------------job no: {count}------------{job["job_url"]} -------'

        if not Jobs.objects.filter(job_id=job['job_id'], company=company_obj) and len(job['location']):
            print(f'-have-', sep='', end='')
            logging_str += f'-have-'

            # Find Locations Objects from database

            city = job['location'].split(',')[0].strip()
            country = 'India'

            try:
                location_obj = Locations.objects.get(city=city, country=country)
            except:

                location_obj = Locations.objects.get_or_create(city=city, country=country)
                try:
                    for_iso_codes = Locations.objects.get(country=country)

                    location_obj.country_code_iso2 = for_iso_codes.country_code_iso2
                    location_obj.country_code_iso3 = for_iso_codes.country_code_iso3
                except:
                    print(f'-Error in Iso Codes-')
                    logging_str += f'-Error in Iso Codes-'
                location_obj.save()

                print(f'-Error in locations-', sep='', end='')
                logging_str += f'-Error in locations-'

            job_locations_objects.append(location_obj)

            print(f'-Locations: {[location.id for location in job_locations_objects]}-', sep='', end='')
            logging_str += f'-Locations: {[location.id for location in job_locations_objects]}-'

            driver.get(job['job_url'])

            try:
                WebDriverWait(driver, 10).until(EC.url_to_be(base_url))
            except:
                print("page is taking so much time to load")

            if driver.current_url == job['job_url']:
                # Extracting Post Data
                post = ''
                total_no_of_divs_in_a_post = len(driver.find_elements(By.XPATH,
                                                                      '//*[@id="content"]/div/section[1]/div[2]/div/div/div/*[@class="ng-scope"]'))
                try:
                    for div_count in range(1, total_no_of_divs_in_a_post + 1):
                        element = driver.find_elements(By.XPATH,
                                                       f'//*[@id="content"]/div/section[1]/div[2]/div/div/div/div[{div_count}]')
                        text = element[0].text
                        # print(text)
                        if text == '':
                            continue
                        if div_count == 1:
                            post += text + '\n\n\n'
                        else:
                            post += text + '\n'

                        if div_count != 1:
                            if 'Department' in text:
                                category = text.split(':')[1]
                                category = category.replace('\n', '')

                            if 'Years Of Exp' in text:
                                required_experience = int(text.split(':')[1].split(' ')[0])

                            if 'Posted On' in text:
                                posting_date = text.split(':')[1].strip('\n') + ' 00:00'
                                posting_date = timezone.datetime.strptime(posting_date, '%d-%b-%Y %H:%M').strftime(
                                    '%Y-%m-%d %H:%M')
                except:
                    print(f'-Error In Post-', end='', sep='')
                    logging_str += f'-Error In Post-'
                    continue

                try:
                    new_job_obj = Jobs(title=data[keys]['title'], date=data[keys]['posted_date'], post=post,
                                       job_url=data[keys]['job_url'], job_id=data[keys]['job_id'], company=company_obj,
                                       category=category, required_experience=required_experience, reviewed=True)

                    new_job_obj.save()
                    new_job_obj.date = posting_date
                    new_job_obj.save()

                    # adding locations
                    for loc in job_locations_objects:
                        new_job_obj.location.add(loc)

                    # adding skills
                    add_skill(new_job_obj)

                    print(f'-saved into database-', end='', sep='')
                    logging_str += f'-saved into database-'

                except:
                    print('-job post Error -', sep='', end='')
                    logging_str += '-job post Error -'

            else:
                print(f'-Not Saved into database-', sep='', end='')
                logging_str += f'-Not Saved into database-'
        else:
            if len(job['location']):
                print('-already in database-', sep='', end='')
                logging_str += '-already in database-'
            else:
                print('-not have location-', sep='', end='')
                logging_str += '-not have location-'

        count = count + 1

        logging_str += '\n'
        print()

        logging_file = open(daily_jobs_info_file, mode='a')
        logging_file.write(logging_str)
        logging_file.close()

    logging_file = open(f'logging/{company_obj.name.lower()}/start_up_end/{company_obj.name.lower()}_logging.txt',
                        mode='a')
    logging_file.write(
        f"---------------------Update {company_obj.name} Jobs Ended {timezone.datetime.now()}----------------------\n\n")
    logging_file.close()
    f"---------------------Update {company_obj.name} Jobs Ended {timezone.datetime.now()}----------------------\n\n"
    driver.close()


def startup():
    print(f"---------------------Update Jobs Command Started {timezone.datetime.now()}----------------------\n")

    try:
        logging_file = open('logging/start_up_end/daily_startup_and_close.txt', mode='a')
    except:
        path = str(settings.BASE_DIR) + '/logging/start_up_end'
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)
            print(f"The new directory is created!: {path}")

        logging_file = open('logging/start_up_end/daily_startup_and_close.txt', mode='a')

    logging_file.write(
        f"---------------------Update Jobs Command Started {timezone.datetime.now()}----------------------\n")
    logging_file.close()

    companies = Company.objects.all()

    for i in companies:
        try:
            globals()[(i.name.lower()).replace(' ', '_')](i.career_page, i)
        except:
            print(" Error Inside i.name.lower()).replace(' ', '_') ")
            logging_file = open('logging/start_up_end/daily_startup_and_close.txt', mode='a')
            logging_file.write(
                f"--------------------- Error Inside i.name.lower()).replace(' ', '_') {timezone.datetime.now()}----------------------\n")
            logging_file.close()

    new_jobs_status = JobsStats.objects.filter(date__gt=timezone.datetime.today()).first()

    if not new_jobs_status:
        new_jobs_status = JobsStats()

    new_jobs_status.total_available = Jobs.objects.filter(available=True).count()
    new_jobs_status.total_unavailable = Jobs.objects.filter(available=False).count()
    new_jobs_status.save()

    print(f"---------------------Update Jobs Command Ended {timezone.datetime.now()}----------------------")

    logging_file = open('logging/start_up_end/daily_startup_and_close.txt', mode='a')
    logging_file.write(
        f"---------------------Update Jobs Command Ended {timezone.datetime.now()}----------------------\n")
    logging_file.close()

    sleep_time = random.randint(50400, 82800)
    print(f'Waiting for {sleep_time % (24 * 3600)}')
    time.sleep(sleep_time)

    startup()


class Command(BaseCommand):
    def handle(self, *args, **options):
        startup()
