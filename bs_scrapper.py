from selenium import webdriver
import time
from bs4 import BeautifulSoup
import os
import json
import urllib.request
from selenium.common.exceptions import NoSuchElementException

CONFIG = {'username': "tarikhsazan", "password": "koosha123", "instagram_profile": "tah"}


def write_file(dic, CONFIG):
    """accept dictionary serialize and save it to json file in its folder"""
    dic = json.dumps(dic, indent=4)
    os.mkdir(os.path.join('bs_data', CONFIG['instagram_profile']))
    file_name = CONFIG['instagram_profile'] + '.json'
    complete_name = os.path.join(os.path.join('bs_data', CONFIG['instagram_profile']), file_name)
    with open(complete_name, 'w') as f:
        f.write(dic)


def replacement(s):
    s = s.replace('null', 'None')
    s = s.replace('false', 'False')
    s = s.replace('true', 'True')
    return s


if __name__ == "__main__":
    d = {
        "name": "koosha",
        "age": 32,
        "occupation": "programmer"
    }
    write_file(d, CONFIG)
    url = "https://www.instagram.com/accounts/login/"
    driver = webdriver.Chrome()
    driver.get(url)

    driver.find_element_by_xpath("//input[@name='username']").send_keys(CONFIG['username'])
    driver.find_element_by_xpath("//input[@name='password']").send_keys(CONFIG['password'])
    driver.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(5)

    # notification dialog
    try:
        driver.find_element_by_xpath("//div[@role='dialog']")
        driver.find_element_by_class_name('HoLwm').click()
    except NoSuchElementException:
        print('No notification  check')

    url = "https://www.instagram.com/" + CONFIG['instagram_profile']
    driver.get(url)
    time.sleep(3)
    # TODO: start new thread for scrolling and another tread for downloading the content

    # scroll to the bottom of page
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while not match:
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == lenOfPage:
            match = True

    # find all links on the page and if they match '/p' append to list named posts
    posts = []
    links = driver.find_elements_by_tag_name('a')
    print(links)
    print(len(links))
    for link in links:
        post = link.get_attribute('href')
        if '/p/' in post:
            posts.append(post)

    posts = [p + '?__a=1' for p in posts]

    for p in posts:
        driver.get(p)
        soup = BeautifulSoup(driver.page_source)
        dic = eval(replacement(soup.select('pre')[0].get_text()))
        post_type = dic['graphql']['shortcode_media']['__typename']
        if post_type == 'GraphImage':
            pass
