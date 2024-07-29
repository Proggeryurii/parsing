import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def parse_hh_vacancies(keywords, areas):
    # Настройка ChromeOptions
    chrome_options = Options()
     # Запуск браузера в фоновом режиме
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Запуск браузера с использованием ChromeDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    base_url = 'https://spb.hh.ru/search/vacancy'
    vacancies = []

    for area in areas:
        params = {
            'text': 'python',
            'area': area,
            'page': 0
        }

        driver.get(base_url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

        items = soup.find_all('div', class_='vacancy-serp-item__layout')
        if not items:
            continue

        for item in items:
            # Получаем ссылку на вакансию
            link_tag = item.find('a', class_='serp-item__title')
            link = link_tag['href'] if link_tag else 'Не указана'

            # Получаем название вакансии
            title = link_tag.text.strip() if link_tag else 'Не указано'

            # Получаем название компании
            company_tag = item.find('a', class_='bloko-link_kind-tertiary')
            company = company_tag.text.strip() if company_tag else 'Не указана'

            # Получаем город
            city_tag = item.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
            city = city_tag.text.strip() if city_tag else 'Не указан'

            # Получаем зарплатную вилку, если указана
            salary_tag = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            salary = salary_tag.text.strip() if salary_tag else 'Не указана'

            # Переходим на страницу вакансии и проверяем описание
            driver.get(link)
            vacancy_page_source = driver.page_source
            vacancy_soup = BeautifulSoup(vacancy_page_source, 'lxml')
            vacancy_description_tag = vacancy_soup.find('div', {'data-qa': 'vacancy-description'})
            vacancy_description = vacancy_description_tag.text if vacancy_description_tag else ''

            # Проверяем наличие ключевых слов в описании
            if all(keyword.lower() in vacancy_description.lower() for keyword in keywords):
                vacancy_info = {
                    'link': link,
                    'title': title,
                    'company': company,
                    'city': city,
                    'salary': salary
                }
                vacancies.append(vacancy_info)

    driver.quit()
    return vacancies


# Задаем ключевые слова для поиска в описании вакансии
keywords = ['django', 'flask']

# Задаем области для поиска вакансий (1 - Москва, 2 - Санкт-Петербург)
areas = [1, 2]

# Парсим вакансии с первой страницы и выводим результат в JSON
vacancies = parse_hh_vacancies(keywords, areas)
print(json.dumps(vacancies, ensure_ascii=False, indent=2))

