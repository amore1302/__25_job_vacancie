import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


def get_table_vscsncie(title, cur__rating):
    main_title = "{0}\nЯзык программирования".format(title)
    table_data = [[ main_title,
                    "Вакансий найдено",
                    "Вакансий обработано",
                    "Средняя зарплата"]]

    for key, current_vacancie in cur__rating.items():
        current_row_table = [key, current_vacancie["vacancies_found"], current_vacancie["vacancies_processed"],
                            current_vacancie["average_salary"]]
        table_data.append(current_row_table)

    return AsciiTable(table_data)

def predict_rub_salary(salary_min,salary_max):
    find_min = False
    find_max = False

    if salary_min != None:
        if salary_min > 0:
            find_min = True

    if salary_max != None:
        if salary_max > 0:
            find_max = True

    if (not find_min ) and (not find_max):
        return None
    if find_min  and find_max :
        return int((salary_min + salary_max) / 2)

    if find_max :
        return int(salary_max * 0.8)

    return int(salary_min * 1.2)


def predict_rub_salary_sj(current_vacancie):
    currency = current_vacancie["currency"]
    if currency != "rub":
        return None
    salary_min = current_vacancie["payment_from"]
    salary_max = current_vacancie["payment_to"]
    return predict_rub_salary(salary_min,salary_max)


def predict_rub_salary_hh(current_vacancie):
    salary_vacancie = current_vacancie["salary"]
    if salary_vacancie == None:
        return None
    currency = salary_vacancie["currency"]
    if currency != "RUR":
        return None
    salary_min = salary_vacancie["from"]
    salary_max = salary_vacancie["to"]
    return predict_rub_salary(salary_min,salary_max)


def get_sj_rating_current_language(sj__rating, current_language):

    vacancies_processed = 0
    total_summa_vacancies = 0.0
    current_name_vacancie = "программист {0}".format(current_language)

    headers = {"X-Api-App-Id": secret_key_superjob
               }

    payload = {"town": "4"
        , "catalogues": "48"
        , "count": "100"
        , "not_archive": "1"
        , "keyword": current_name_vacancie
               }
    host_api = "https://api.superjob.ru/2.0/vacancies/"
    response = requests.get(host_api, headers=headers, params=payload)
    response.raise_for_status()
    find_vacancies = response.json()

    job_found = find_vacancies["total"]
    job_vacancies = find_vacancies["objects"]
    next_page = find_vacancies["more"]
    current_rating = {}
    current_rating["vacancies_found"] = job_found
    current_page = 0
    while True:
        if current_page > 0:
            payload["page"] = current_page
            response = requests.get(host_api, headers=headers, params=payload)
            response.raise_for_status()

            job_vacancies = find_vacancies["objects"]
            next_page = find_vacancies["more"]

        for current_vacancie in job_vacancies:
            try:
                current_salary = predict_rub_salary_sj(current_vacancie)
            except:
                current_salary = None
            if current_salary == None:
                continue
            vacancies_processed = vacancies_processed + 1
            total_summa_vacancies = total_summa_vacancies + current_salary

        if not next_page :
            break
        current_page = current_page + 1

    current_rating["vacancies_processed"] = vacancies_processed
    average_salary = 0
    if vacancies_processed > 0:
        average_salary = total_summa_vacancies / vacancies_processed
        average_salary = int(average_salary)
    current_rating["average_salary"] = average_salary
    sj__rating[current_language] = current_rating


def get_hh_rating_current_language(hh__rating, current_language):

    vacancies_processed = 0
    total_summa_vacancies = 0.0
    current_name_vacancie = "программист {0}".format(current_language)

    host_api = 'https://api.hh.ru/vacancies'
    payload = {"text": current_name_vacancie
        , "area": "1"
        , "period": "30"
               }
    response = requests.get(host_api, params=payload)
    response.raise_for_status()

    find_vacancies = response.json()
    job_vacancies = find_vacancies["items"]
    job_found = find_vacancies["found"]
    all_pages = find_vacancies["pages"]
    per_page = find_vacancies["per_page"]
    current_rating = {}
    current_rating["vacancies_found"] = job_found
    payload["per_page"] = per_page
    for current_page in range(all_pages):
        if current_page > 0:
            payload["page"] = current_page
            response = requests.get(host_api, params=payload)
            response.raise_for_status()

            find_vacancies = response.json()
            job_vacancies = find_vacancies["items"]

        for current_vacancie in job_vacancies:
            try:
                current_salary = predict_rub_salary_hh(current_vacancie)
            except:
                current_salary = None
            if current_salary == None:
                continue
            vacancies_processed = vacancies_processed + 1
            total_summa_vacancies = total_summa_vacancies + current_salary

    current_rating["vacancies_processed"] = vacancies_processed
    average_salary = 0
    if vacancies_processed > 0:
        average_salary = total_summa_vacancies / vacancies_processed
        average_salary = int(average_salary)
    current_rating["average_salary"] = average_salary
    hh__rating[current_language] = current_rating


def get_hh_rating(Programming_languages, hh__rating):
    for current_language in Programming_languages:
        get_hh_rating_current_language(hh__rating, current_language)


def get_sj_rating(Programming_languages, sj__rating):
    for current_language in Programming_languages:
        get_sj_rating_current_language(sj__rating, current_language)

def main():
    Programming_languages = [
        "javaScript"
        "Java" ,
        "python" ,
        "ruby" ,
        "php" ,
        "c++" ,
        "c#" ,
        "c" ,
        "go" ,
        "objective-c" ,
        "scala" ,
        "swift" ,
    ]

    hh__rating = {}
    try:
        get_hh_rating(Programming_languages, hh__rating)
    except requests.exceptions.HTTPError as error:
        exit("Не смогли получить данных с сервиса hh:\n{0}".format(error))
    sj__rating = {}
    try:
        get_sj_rating(Programming_languages, sj__rating)
    except requests.exceptions.HTTPError as error:
        exit("Не смогли получить данных с сервиса super job:\n{0}".format(error))
    table_hh = get_table_vscsncie("Hh Moscow", hh__rating)
    table_sj = get_table_vscsncie("SuperJob Moscow", sj__rating)
    print(table_hh.table)
    print(table_sj.table)

if __name__ == '__main__':
    load_dotenv()
    secret_key_superjob = os.getenv("SECRET_KEY_SUPERJOB")
    main()
