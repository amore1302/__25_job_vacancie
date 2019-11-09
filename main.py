import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable

def out_table_terminal(title, cur__rating):
  main_title = "{0}\nЯзык программирования".format(title)
  table_data  = [ [main_title, "Вакансий найдено","Вакансий обработано" ,"Средняя зарплата" ] ]

  for key, curent_vacancie in cur__rating.items():
    curent_row_table = [ key, curent_vacancie["vacancies_found"], curent_vacancie["vacancies_processed"], curent_vacancie["average_salary"]]
    table_data.append(curent_row_table)

  table = AsciiTable(table_data)
  print(table.table)


def predict_rub_salary_sj(curent_vacancie):
  valuta = curent_vacancie["currency"]
  if valuta != "rub":
    return None

  find_min = False
  find_max = False

  salary_min = curent_vacancie["payment_from"]
  if salary_min != None:
      if salary_min > 0:    
        find_min = True

  salary_max = curent_vacancie["payment_to"]
  if salary_max != None:
      if salary_max > 0:    
        find_max = True

  if (find_min == False) and (find_max == False):
    return None
  if (find_min == True) and (find_max == True):
    return int( (salary_min + salary_max )/2 )

  if (find_max == True):
    return int(salary_max * 0.8)

  return int( salary_min * 1.2 )

def predict_rub_salary(curent_vacancie):
  salary_vacancie = curent_vacancie["salary"]
  if salary_vacancie == None:
    return None
  valuta = salary_vacancie["currency"]
  if valuta != "RUR":
    return None
  find_min = False
  find_max = False

  salary_min = salary_vacancie["from"]
  if salary_min != None:
      if salary_min > 0:    
        find_min = True

  salary_max = salary_vacancie["to"]
  if salary_max != None:
      if salary_max > 0:    
        find_max = True
  
  if (find_min == False) and (find_max == False):
    return None
  if (find_min == True) and (find_max == True):
    return int( (salary_min + salary_max )/2 )

  if (find_max == True):
    return int(salary_max * 0.8)

  return int( salary_min * 1.2 )



def get_sj_rating_curent_language(sj__rating,curent_language):
  print(curent_language)

  vacancies_processed = 0
  summa_vacancies_processed = 0.0
  curent_name_vacancie = "программист {0}".format(curent_language)


  headers = {   "X-Api-App-Id" : SECRET_KEY_SUPERJOB
   }


  payload = { "town":"4"
          ,"catalogues":"48"
          ,"count":"100"
          ,"not_archive":"1"
          ,"keyword":curent_name_vacancie
  }
  host_api = "https://api.superjob.ru/2.0/vacancies/"
  response = requests.get(host_api, headers=headers , params=payload)
  response.raise_for_status()
  if response.status_code != 200 :
    print("Не Получили хороший результат от api.superjob.ru сод Ответа = {0}".format(response.status_code))
    exit()

  find_vacancies = response.json()

  job_found = find_vacancies["total"]
  job_vacancies = find_vacancies["objects"]
  next_page = find_vacancies["more"]
  curent_rating = {}
  curent_rating["vacancies_found"] = job_found
  curent_page = 0
  while True == True :
    if curent_page > 0 :
      payload["page"] = curent_page
      response = requests.get(host_api, headers=headers , params=payload)
      response.raise_for_status()
      if response.status_code != 200 :
        print("Не Получили хороший результат от api.superjob.ru сод Ответа = {0}".format(response.status_code))
        exit()
      job_vacancies = find_vacancies["objects"]
      next_page = find_vacancies["more"]

    for curent_vacancie in job_vacancies:
      try:
        curent_salary = predict_rub_salary_sj(curent_vacancie)
      except:
       curent_salary = None
      if curent_salary == None:
        continue
      vacancies_processed = vacancies_processed + 1
      summa_vacancies_processed = summa_vacancies_processed + curent_salary

    if next_page == False:
      break
    curent_page = curent_page + 1

  curent_rating["vacancies_processed"] = vacancies_processed
  average_salary = 0
  if vacancies_processed > 0 :
    average_salary = summa_vacancies_processed / vacancies_processed
    average_salary = int(average_salary)
  curent_rating["average_salary"] = average_salary
  sj__rating[curent_language] = curent_rating


def get_hh_rating_curent_language(hh__rating,curent_language):
  print(curent_language)

  vacancies_processed = 0
  summa_vacancies_processed = 0.0
  curent_name_vacancie = "программист {0}".format(curent_language)

  host_api = 'https://api.hh.ru/vacancies'
  payload = {"text": curent_name_vacancie
          ,"area":"1"
          ,"period":"30"
          }
  response = requests.get(host_api, params=payload)
  response.raise_for_status()
  if response.status_code != 200 :
    print("Не Получили хороший результат от api.hh.ru сод Ответа = {0}".format(response.status_code))
    exit()

  find_vacancies = response.json()
  job_vacancies  = find_vacancies["items"]
  job_found  = find_vacancies["found"]
  all_pages = find_vacancies["pages"]
  per_page = find_vacancies["per_page"]
  curent_rating = {}
  curent_rating["vacancies_found"] = job_found
  payload["per_page"] = per_page
  for curent_page in range(all_pages):
    print(curent_page)
    if curent_page > 0 :
      payload["page"] = curent_page
      response = requests.get(host_api, params=payload)
      response.raise_for_status()
      if response.status_code != 200 :
        print("Не Получили хороший результат от api.hh.ru сод Ответа = {0}".format(response.status_code))
        exit()
      find_vacancies = response.json()
      job_vacancies  = find_vacancies["items"]

    for curent_vacancie in job_vacancies:
      try:
        curent_salary = predict_rub_salary(curent_vacancie)
      except:
       curent_salary = None
      if curent_salary == None:
        continue
      vacancies_processed = vacancies_processed + 1
      summa_vacancies_processed = summa_vacancies_processed + curent_salary

  curent_rating["vacancies_processed"] = vacancies_processed
  average_salary = 0
  if vacancies_processed > 0 :
    average_salary = summa_vacancies_processed / vacancies_processed
    average_salary = int(average_salary)
  curent_rating["average_salary"] = average_salary
  hh__rating[curent_language] = curent_rating


def get_hh_rating(Programming_languages, hh__rating):
  for curent_language in Programming_languages:
    get_hh_rating_curent_language(hh__rating,curent_language)

def get_sj_rating(Programming_languages, sj__rating):
  for curent_language in Programming_languages:
    get_sj_rating_curent_language(sj__rating,curent_language)    

Programming_languages = [
  "javaScript"
  ,"Java"
  ,"python"
  ,"ruby"
  ,"php"
  ,"c++"
  ,"c#"
  ,"c"
  ,"go"
  ,"objective-c"
  ,"scala"
  ,"swift"
]


load_dotenv()
SECRET_KEY_SUPERJOB = os.getenv("SECRET_KEY_SUPERJOB")
hh__rating = {}
get_hh_rating(Programming_languages, hh__rating)
sj__rating = {}
get_sj_rating(Programming_languages, sj__rating)
out_table_terminal("Hh Moscow", hh__rating)
out_table_terminal("SuperJob Moscow", sj__rating)

