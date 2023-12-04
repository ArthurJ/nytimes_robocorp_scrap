import re
import logging

import configparser

from time import sleep

from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Excel.Files import Files

from nyt_resources import *

from playwright._impl._api_types import TimeoutError


config = configparser.ConfigParser()
config.read('config.txt')

search_phrase = config.get('DEFAULT','search_phrase')
months = int(config.get('DEFAULT','months'))
sections = config.get('DEFAULT','sections').split(',')

http_lib = HTTP()
excel_lib = Files()


@task
def challenge():
    browser.configure(
        # headless=True,
        slowmo=100  # The results are more reliable with a little slowmo
    )
    browser.page().set_viewport_size({'width':1800, 'height':1200})
    open_site()
    search(search_phrase, months, sections)
    get_result_list(search_phrase)
    # sleep(60)
        

def open_site():
    browser.goto('https://www.nytimes.com')
    page = browser.page()
    unclog(page)


def unclog(page):
    if page.is_visible(BTN_CONTINUE):
        page.click(BTN_CONTINUE)
    if page.is_visible(BTN_REJECT):
        page.click(BTN_REJECT)


def search(search_phrase, months, sections):   
    start_search(search_phrase)
    set_date(months)
    set_sections(sections)
    sortbynewest()


def start_search(search_phrase):
    page = browser.page()
    page.click(BTN_SEARCH)
    page.fill(INPUT_SEARCH, search_phrase)
    page.click(BTN_SUBMIT)


def set_date(months):
    page = browser.page()
    page.click(BTN_DATE_DROPDOWN)
    page.click(BTN_SPECIFIC_DATES)
    if months in [0, 1]:
        page.click(CAL_FIRST_DAY)
        page.click(BTN_NEXT_MONTH)
        page.click(CAL_FIRST_DAY)
    else:
        for i in range(months-1):
            page.click(BTN_PREV_MONTH)
        page.click(INPUT_START_DATE)
        page.click(CAL_FIRST_DAY)

        page.click(BTN_DATE_DROPDOWN)
        page.click(BTN_DATE_DROPDOWN)
        page.click(BTN_SPECIFIC_DATES)

        page.click(BTN_NEXT_MONTH)
        page.click(INPUT_END_DATE)
        page.click(CAL_FIRST_DAY)



def set_sections(sections):
    if not sections: return
    page = browser.page()
    page.click(BTN_SECTION_DROPDOWN)
    for section in sections:
        section_path = BTN_SECTION.format(section)
        if page.is_visible(section_path):
            page.click(section_path)
    page.click(BTN_SECTION_DROPDOWN)


def sortbynewest():
    page = browser.page()
    page.select_option(BTN_SORT_DROPDOWN, "newest")
    sleep(3)


def get_result_list(search_phrase):
    page = browser.page()
    unclog(page)
    
    start_date = page.locator(BTN_DATE_DISPLAY).get_attribute('value').split('\xa0–\xa0')[0].split('/')
    start_date = ''.join([start_date[-1], start_date[0], start_date[1]])
    
    while True:
        locator = page.locator(RESULT_LIST)
        item_date = get_crude_date(locator.last, start_date)

        if int(item_date)<int(start_date):
            break
        
        if page.is_visible(BTN_SHOW_MORE):
            page.click(BTN_SHOW_MORE)
        else:
            break
    
    logging.info(f'Page:\t{page.url}')
    locator = page.locator(RESULT_LIST)

    wb = create_excel()

    for idx, iloc in enumerate(locator.all(), start=2):
        if int(get_crude_date(iloc, start_date))<int(start_date):
            logging.info(f'\tRejected Title: {get_title(iloc)}')
            logging.info(f'\tRejected Date: {get_date(iloc)}')
            continue
        #iloc.screenshot(path=f'output/screenshots/{search_phrase.lower().replace(" ", "_")}/{idx}.png')
        
        img_url = get_img_url(iloc)
        img_filename = get_img_filename(img_url)
        
        save_img(img_url, img_filename)
        
        populate_excel(wb, idx, iloc, img_filename, search_phrase)

    wb.save()


def save_img(img_url, img_filename):
    if img_url:
        http_lib.download(img_url,
                         overwrite=True, 
                         target_file=f'output/{img_filename}')

def create_excel():
    wb = excel_lib.create_workbook(path='output/nyt_report.xlsx')
    wb.create_worksheet('NYT_Scrapper')
    
    wb.set_cell_value(row=1, column=1, value='Title')
    wb.set_cell_value(row=1, column=2, value='Date')
    wb.set_cell_value(row=1, column=3, value='Description')
    wb.set_cell_value(row=1, column=4, value='Picture Filename')
    wb.set_cell_value(row=1, column=5, value='Search phrase count')
    wb.set_cell_value(row=1, column=6, value='Mentions money')
    
    return wb

def populate_excel(wb, row, item_locator, img_filename, search_phrase):
    wb.set_cell_value(row, column=1, value=get_title(item_locator))
    wb.set_cell_value(row, column=2, value=get_date(item_locator))
    wb.set_cell_value(row, column=3, value=get_description(item_locator))
    wb.set_cell_value(row, column=4, value=img_filename)
    wb.set_cell_value(row, column=5, value=get_desc_search_count(item_locator, search_phrase))
    wb.set_cell_value(row, column=6, value=says_money(item_locator))


def get_crude_date(item_locator, current_date):
    found_date = get_date(item_locator)
    if found_date:
        splitted_date = found_date.split('/')
        return ''.join(splitted_date)
    return current_date


def get_date(item_locator):
    date_re = re.compile(DATE_RE)
    a_url = item_locator.locator(A_TAG).get_attribute('href')
    found = date_re.search(a_url)
    if found:
        return found.group('date')
    else:
        browser.page().set_default_timeout(150)
        try:
            image_url = item_locator.locator(IMG_TAG).get_attribute('src')
            found = date_re.search(image_url)
            if found: 
                return found.group('date')
        except TimeoutError as e:
            pass
        finally:
            browser.page().set_default_timeout(30_000)
    return None


def get_img_url(item_locator):
    item_locator.scroll_into_view_if_needed()
    img_locator = item_locator.locator(IMG_TAG)
    if img_locator.is_visible():
        return item_locator.locator(IMG_TAG).get_attribute('src')
    return ''


def get_img_filename(url):
    if url:
        file_name = re.search(IMG_FILENAME_RE, url).group(FILENAME_GROUP_NAME)
        return file_name    
    return ''


def get_title(item_locator):
    return item_locator.locator(TITLE_TAG).inner_text()


def get_description(item_locator):
    desc_locator = item_locator.locator(DESCRIPTION_TAG)
    if desc_locator.is_visible():
        return desc_locator.inner_text()
    return ''


def get_desc_search_count(item_locator, search_phrase):
    fulltext = f'{get_description(item_locator)}\n{get_title(item_locator)}'
    return len(re.findall(search_phrase, fulltext))


def says_money(item_locator):
    fulltext = f'{get_description(item_locator)}\n{get_title(item_locator)}'
    return len(list(re.findall(MONEY_RE, fulltext))) > 0
