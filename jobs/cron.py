import datetime
import json
import time

from selenium import webdriver
import traceback as tb
import os

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "JobPortal.settings")
django.setup()
# your imports, e.g. Django models
from companies.models import Company
from locations.models import Locations
from jobs.models import Jobs


def browserstack(url, company_obj):
    driver = webdriver.Chrome(executable_path="chromedriver")
    driver.maximize_window()
    driver.get(url)
    locations = driver.find_elements(By.CLASS_NAME, 'location-card-wrapper')
    job_objects = []
    for i in locations:
        # positions, location =
        # print(positions, locations)
        locations_and_position = str(i.text).split('\n')
        remo = '.cls-1{fill:none;}.cls-2{clip-path:url(#clip-path);}.cls-3{fill:#bcbcbb;}.cls-4{' \
               'fill:#fff;}Location_New York'

        if remo in locations_and_position:
            locations_and_position.remove(remo)

        print(locations_and_position)
        location = None
        for count in range(0, len(locations_and_position), 2):
            item = locations_and_position[count]
            positions = locations_and_position[count + 1]
            try:
                City = item.split(',')[0]

                if City == 'Mumbai':
                    location = Locations.objects.get(city=City)
                    location_url = 'mumbai-india'
                if City == 'San Francisco':
                    location = Locations.objects.get(city=City, country='United States')
                    location_url = 'san-francisco-united-states'
                if City == 'Dublin':
                    location = Locations.objects.get(city=City, country='Ireland')
                    location_url = 'dublin-ireland'
                if City == 'US Remote':
                    City = 'Remote'
                    location = Locations.objects.get(city=City, country='United States')
                    location_url = 'us-remote'
                if City == 'New York':
                    location = Locations.objects.get(city=City)
                    location_url = 'new-york'
                if City == 'Atlanta':
                    location = Locations.objects.get(city=City)
                    location_url = 'atlanta'

                print('----------', City, location, '-----------')
                driver.get(url + '/' + location_url)
                category_index = 1
                category = driver.find_elements(By.XPATH, '//*[@id="bd-careers"]/section/div[2]/div[2]/div/div/div[' +
                                                str(category_index) + ']')
                while category:
                    print(category[0].text)
                    category_name = category[0].text
                    driver.get(url + '/' + location_url + '#' + category[0].text.lower())
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

                        job_objects.append({
                            'location': location,
                            'job_url': job_url,
                            'job_id': job_id,
                            'job_title': job,
                            'job_category': category_name
                        })

                        job_index += 1
                        link = driver.find_elements(By.XPATH, '//*[@id="bd-careers"]/section/div[2]/div[3]/div/div['
                                                    + str(category_index) + ']/ul/li[' + str(job_index)
                                                    + ']/a/div/div[2]/button ')
                        job_title = driver.find_elements(By.XPATH,
                                                         '//*[@id="bd-careers"]/section/div[2]/div[3]/div/div['
                                                         + str(category_index) + ']/ul/li[' + str(job_index) +
                                                         ']/a/div/div[''1]/div')

                    time.sleep(10)

                    category_index += 1
                    category = driver.find_elements(By.XPATH,
                                                    '//*[@id="bd-careers"]/section/div[2]/div[2]/div/div/div[' +
                                                    str(category_index) + ']')

            except Exception as error:
                print("error occured : ", error)
                print("trace:{}".format(tb.format_exc().replace("\n", " ")))
    print(job_objects)
    print(len(job_objects))
    total_new_jobs = 0
    for job in job_objects:
        if job['job_id'] and not Jobs.objects.filter(job_id=job['job_id'], company=company_obj):
            driver.get(job['job_url'])
            time.sleep(10)
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
                               job_id=job['job_id'], job_url=job['job_url'], location=job['location'])
                job_obj.save()
                print(job_obj.__dict__)
                print('-----------------------------------------------------------')
                total_new_jobs += 1
    print(total_new_jobs)
    driver.close()


if __name__ == '__main__':

    companies = Company.objects.all()
    for i in companies:
        globals()[i.name.lower()](i.career_page, i)
