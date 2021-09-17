from selenium import webdriver
import time
from bs4 import BeautifulSoup
import os
import json
import urllib.request
from selenium.common.exceptions import NoSuchElementException

CONFIG = {'username': "tarikhsazan", "password": "koosha123", "instagram_profile": "kingbash"}


def write_file(dic, profile_name):
    """accept dictionary serialize and save it to json file in its folder"""
    dic = json.dumps(dic, indent=4)
    # try:
    #     os.mkdir(os.path.join('bs_data', CONFIG['instagram_profile']))
    # except OSError as e:
    #     pass
    file_name = profile_name + '.json'
    complete_name = os.path.join(os.path.join('bs_data', profile_name), file_name)
    with open(complete_name, 'w') as f:
        f.write(dic)


def replacement(s):
    s = s.replace('null', 'None')
    s = s.replace('false', 'False')
    s = s.replace('true', 'True')
    return s


def scroll_to_bottom(driver):
    """scroll the page and in each scroll find the posts that is generated in scrolling and return the post at the
    bottom of the page """
    # scroll to the bottom of page
    len_of_page = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    res = find_posts(driver)
    while not match:
        last_count = len_of_page

        time.sleep(2)
        len_of_page = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        posts = find_posts(driver)
        for p in posts:
            if p not in res:
                res.append(p)
        if last_count == len_of_page:
            match = True
    return res


def login(driver, CONFIG):
    """log in to instagram by the credentials in CONFIG"""
    url = "https://www.instagram.com/accounts/login/"
    driver.get(url)
    driver.find_element_by_xpath("//input[@name='username']").send_keys(CONFIG['username'])
    driver.find_element_by_xpath("//input[@name='password']").send_keys(CONFIG['password'])
    driver.find_element_by_xpath("//button[@type='submit']").click()
    print('signed in instagram')
    time.sleep(5)


def find_posts(driver):
    """find and return posts as a list"""
    page_soup = BeautifulSoup(driver.page_source)
    rows = page_soup.select('.weEfm')
    posts = []
    base_url = 'https://www.instagram.com'
    for r in rows:
        anchors = r.select('a')
        for anchor in anchors:
            posts.append(base_url + anchor['href'])
    return posts


def click_not_now(driver):
    """close save password and notification dialog by clicking not now"""
    print('trying to click on not now if save credential or notification dialog appear')
    print('Please wait it may takes some time')
    # save login info dialog
    try:
        driver.find_element_by_class_name('ABCxa')
        driver.find_element_by_class_name('yWX7d').click()
        print('save log in not now clicked')
    except NoSuchElementException:
        print("save credentials dialog didn't appeared")
    time.sleep(3)

    # notification dialog
    try:
        driver.find_element_by_xpath("//div[@role='dialog']")
        driver.find_element_by_class_name('HoLwm').click()
        print('not now notification clicked')
    except NoSuchElementException:
        print('No notification  check')
    time.sleep(3)


def open_profile(driver, profile_name):
    url = "https://www.instagram.com/" + profile_name
    driver.get(url)
    time.sleep(3)


def get_profile_info(driver):
    """get profile info and return the data in a dictionary"""
    profile_info = driver.find_elements_by_class_name('Y8-fY')
    profile_info = [x.split(' ')[0] for x in [y.text for y in profile_info]]
    profile_info = [int(x.replace(',', "")) for x in profile_info]
    profile_bio = driver.find_element_by_class_name('-vDIg').find_element_by_tag_name('span').text
    return {'profile_name': CONFIG['instagram_profile'],
            'post_count': profile_info[0],
            'followers': profile_info[1],
            'following': profile_info[2],
            'bio': profile_bio,
            'posts': []
            }


def get_post_caption(dic):
    """Get the caption of the post"""
    try:
        caption = dic['graphql']['shortcode_media']['edge_media_to_caption']['edges'][0]['node']['text']
    except IndexError:
        caption = ""
    return caption


def download_file(url, file_name, file_type, profile_name):
    """download the file from the url and save it in bs_data folder and return the path of the file to add to
    json file"""
    if file_type == 'GraphImage':
        file_name += '.jpg'
    else:
        file_name += '.mp4'
    image_path = os.path.join(os.path.join('bs_data', profile_name), file_name)
    urllib.request.urlretrieve(url, image_path)
    return image_path


if __name__ == "__main__":

    driver = webdriver.Chrome()
    login(driver, CONFIG)
    click_not_now(driver)
    open_profile(driver, CONFIG['instagram_profile'])
    # TODO: start new thread for scrolling and another tread for downloading the content
    result = get_profile_info(driver)
    # create new folder for this profile
    try:
        os.mkdir(os.path.join('bs_data', CONFIG['instagram_profile']))
    except OSError as e:
        pass

    posts = scroll_to_bottom(driver)
    # add ?__a=1 make all the data be in a json in pre tag
    posts = [p + '?__a=1' for p in posts]

    for p in posts:
        driver.get(p)
        soup = BeautifulSoup(driver.page_source)
        dic = eval(replacement(soup.select('pre')[0].get_text()))
        post_type = dic['graphql']['shortcode_media']['__typename']
        caption = get_post_caption(dic)
        if post_type == 'GraphImage':
            download_url = dic['graphql']['shortcode_media']['display_url']
            image_name = p.split('/')[-2]
            image_path = download_file(download_url, image_name, post_type, CONFIG['instagram_profile'])

            result['posts'].append({
                'type': post_type,
                'caption': caption,
                'files': [{'type': post_type, 'path': image_path}]
            })
        elif post_type == 'GraphSidecar':

            slides = dic['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
            count = 0
            files = []
            for slide in slides:
                slide_type = slide['node']['__typename']
                image_name = p.split('/')[-2] + f'-{count}'
                count += 1
                if slide_type == 'GraphImage':
                    download_url = slide['node']['display_url']
                    image_path = download_file(download_url, image_name, slide_type, CONFIG['instagram_profile'])
                    files.append({'type': slide_type, 'path': image_path})
                else:
                    download_url = slide['node']['video_url']
                    image_path = download_file(download_url, image_name, slide_type, CONFIG['instagram_profile'])
                    files.append({'type': slide_type, 'path': image_path})
            result['posts'].append(
                {
                    'type': post_type,
                    'caption': caption,
                    'files': files
                }
            )
        else:
            download_url = dic['graphql']['shortcode_media']['video_url']
            video_name = p.split('/')[-2]
            image_path = download_file(download_url, video_name, post_type, CONFIG['instagram_profile'])
            result['posts'].append({
                'type': post_type,
                'caption': caption,
                'files': [{'type': post_type, 'path': image_path}]
            })

    driver.close()
    write_file(result, CONFIG['instagram_profile'])
    print('all images has been downloaded and json file has been saved')
