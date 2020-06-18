import asyncio

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from . import habr_intitial

periods = {'day': '//*[@title="Лучшие публикации за сутки"]', 'week': '//*[@title="Лучшие публикации за неделю"]',
           'month': '//*[@title="Лучшие публикации за месяц"]', 'year': '//*[@title="Лучшие публикации за год"]'}

ratings = {'без_порога': '//*[@title="Все публикации в хронологическом порядке"]',
           '>10': '//*[@title="Все публикации с рейтингом 10 и выше"]',
           '>25': '//*[@title="Все публикации с рейтингом 25 и выше"]',
           '>50': '//*[@title="Все публикации с рейтингом 50 и выше"]',
           '>100': '//*[@title="Все публикации с рейтингом 100 и выше"]', }
lst_pages = []
articles_to_open = []


# start browser
async def get_driver():
    options = Options()
    # options.headless = False = show the browser window
    options.headless = False
    driver = webdriver.Chrome('/home/driver220v/Documents/ChromeDriver/chromedriver', options=options)
    return driver


async def load_initial_page(driver):
    driver.get(habr_intitial)
    wait = WebDriverWait(driver, 10)  # timeout 10 sec
    # wait till the category selector is loaded
    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "tabs")))


async def choose_period(driver, period):
    #

    if period in periods:
        wait = WebDriverWait(driver, 10)  # timeout 10 sec
        wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "toggle-menu")))
        try:
            driver.find_element_by_xpath(periods[period]).click()
            lst_pages.append(driver.current_url)
        except ElementNotInteractableException:
            pass
            # not intractable because it's already clicked

        return True
    else:
        return None


async def choose_rating(driver, rating):
    lst_pages.append(driver.current_url)
    if rating in ratings:

        driver.find_element_by_xpath(ratings[rating]).click()
        return True
    else:
        return None


async def get_pages_amount(driver):
    wait_footer = WebDriverWait(driver, 10)
    # предусмотреть возможность, когда страницы перехода нет
    # и нужно щелкать вручную на каждую страницу
    wait_footer.until(ec.visibility_of_element_located((By.CLASS_NAME, "page__footer")))
    # todo переделать на иф элс???
    try:
        last_page = driver.find_element_by_xpath('//a[@title="Последняя страница"]')
        if last_page:
            last_page.click()
            wait_lat_page = WebDriverWait(driver, 10)
            wait_lat_page.until(ec.visibility_of_element_located((By.CLASS_NAME, "posts_list")))
            html = driver.execute_script('return document.documentElement.outerHTML')
            soap = BeautifulSoup(html, 'lxml')
            last_page_tag = soap.find('span',
                                      class_='toggle-menu__item-link toggle-menu__item-link_pagination '
                                             'toggle-menu__item-link_active')
            # здесь иногда выдает None type object has no attribute getText()
            print(last_page_tag)
            last_page_int = int(last_page_tag.getText())

        else:
            return False
    except NoSuchElementException:
        html = driver.execute_script('return document.documentElement.outerHTML')
        soap = BeautifulSoup(html, 'lxml')

        li_pages = soap.find('ul', class_="toggle-menu toggle-menu_pagination")
        last_page_int = int(li_pages.find_all('a')[-1].getText())

    for page_number, _ in enumerate(range(last_page_int - 1), 2):
        lst_pages.append(f'page{page_number}')

    return True


async def split_url(cur_url):
    split_url_lst = cur_url.split('/')
    return split_url_lst


# async def find_content(driver, session, url):
#     async with session.get(f'{url}') as resp:
#         try:
#             print(await resp.text())
#         except Exception as e:
#             print(url)
#             print(e)

# driver.execute_script("window.open('');")
# try:
#     driver.get(url)
# except Exception as e:
#     print(url)
#     print(e)


async def fetch_url(url, session):
    async with session.get(f'{url}') as resp:
        soup = BeautifulSoup(await resp.text(), features="lxml")
        # soap = pages with href's leading to articles
        for anchor_links in soup.find_all('a', class_="post__title_link"):
            href = anchor_links.get('href')
            print(href)
            articles_to_open.append(href)


async def create_tasks(urls):
    semaphore = asyncio.Semaphore(100)
    tasks = []
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            for url in urls:
                task = asyncio.create_task(fetch_url(url, session))
                tasks.append(task)

            await asyncio.gather(*tasks)

    # async with aiohttp.ClientSession() as session_fetch:
    #     tasks_articles = []
    #     for article in articles_to_open:
    #         task_open = asyncio.create_task(find_content(driver, session_fetch, article))
    #         tasks_articles.append(task_open)
    #     await asyncio.gather(*tasks_articles)


async def task_manager(driver):
    pages_to_open = []
    cur_url = driver.current_url
    split_url_lst = await split_url(cur_url)

    element_name = None
    for entry in split_url_lst:
        if entry.startswith('page'):
            element_name = entry
            break

    for i in lst_pages:
        new_url = cur_url.replace(f"{element_name}", f'{i}')
        pages_to_open.append(new_url)
    return pages_to_open


async def find_articles_main(entry_word, entry_class, entry_phrase):
    driver = await get_driver()
    await load_initial_page(driver)
    # if user has chosen category best
    if entry_word == 'best':

        # find element which is responsible for "Лучшие"
        driver.find_element_by_xpath('//a[@href="https://habr.com/ru/top/"]').click()
        is_clicked = await choose_period(driver, entry_class)
        if is_clicked is not True:
            return False

    elif entry_word == 'all':
        # find element which is responsible for "Все подряд"
        driver.find_element_by_xpath('//a[@href="https://habr.com/ru/all/"]').click()
        is_clicked = await choose_rating(driver, entry_class)
        if is_clicked is not True:
            return False
    else:
        return False

    got_pages = await get_pages_amount(driver)
    if got_pages is True:
        pages_to_open = await task_manager(driver)

        await create_tasks(pages_to_open)
