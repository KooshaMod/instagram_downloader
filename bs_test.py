from selenium import webdriver
import time
from bs4 import BeautifulSoup


if __name__ == "__main__":
    username = "tarikhsazan"
    password = "koosha123"

    getdriver = ("https://www.instagram.com/accounts/login/")

    driver = webdriver.Chrome()
    driver.get(getdriver)

    driver.find_element_by_xpath("//input[@name='username']").send_keys(username)
    driver.find_element_by_xpath("//input[@name='password']").send_keys(password)
    driver.find_element_by_xpath("//button[@type='submit']").click()
