from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

CONFIG = {'username': "tarikhsazan", "passowrd": "koosha123", "instagram_profile": "kingbash"}
if __name__ == "__main__":

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
