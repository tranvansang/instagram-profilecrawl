"""Methods to extract the data for the given usernames profile"""
from time import sleep
from re import findall
import math
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import requests
from util.settings import Settings
from .util import web_adress_navigator
import datetime

from PIL import Image
import urllib.request
import ssl
import io
from html.parser import HTMLParser

def getImageSize(url):
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context) as u:
       f = io.BytesIO(u.read())
       img = Image.open(f)
    return img.size

def get_user_info(browser):
    """Get the basic user info from the profile screen"""

    container = browser.find_element_by_class_name('v9tJq')
    print("ok")
    img_container = browser.find_element_by_class_name('RR-M-')
    infos = container.find_elements_by_class_name('Y8-fY ')
    alias_name = container.find_element_by_class_name('-vDIg') \
        .find_element_by_tag_name('h1').text
    try:
        bio = container.find_element_by_class_name('-vDIg') \
            .find_element_by_tag_name('span').text
    except:
        print("\nBio is empty")
        bio = ""
    try:
        bio_url = container.find_element_by_class_name('yLUwa').text
    except:
        print("\nBio Url is empty")
        bio_url = ""
    print("\nalias name: ", alias_name)
    print("\nbio: ", bio)
    print("\nurl: ", bio_url, "\n")
    prof_img = img_container.find_element_by_tag_name('img').get_attribute('src')
    num_of_posts = extract_exact_info(infos[0])
    followers = extract_exact_info(infos[1])
    following = extract_exact_info(infos[2])

    return alias_name, bio, prof_img, num_of_posts, followers, following, bio_url


def extract_exact_info(info):
    exact_info = 0
    try:
        exact_info = int(info.find_element_by_tag_name('span').get_attribute('title').replace('.', '').replace(',', ''))
    except:
        exact_info = str(info.text.split(' ')[0].replace(',', ''))
        if exact_info.find('.') != -1:
            exact_info = exact_info.replace('.', '')
            exact_info = int(exact_info.replace('k', '00').replace('m', '00000'))
        else:
            exact_info = int(exact_info.replace('k', '000').replace('m', '000000'))
    return exact_info


def extract_post_info(browser):
    """Get the information from the current post"""

    post = browser.find_element_by_tag_name('article')
    imgs = post.find_elements_by_tag_name('img')

    for element in imgs:
        className = element.get_attribute('class')
        if ( className == 'FFVAD'):
            alt = element.get_attribute('alt')
            img = element.get_attribute('src')
            srcset = element.get_attribute('srcset')
            #width, height = getImageSize(img)
            sizes = element.get_attribute('sizes')
            break
    
    caption = ''
    divs = post.find_elements_by_tag_name('div')
    for element in divs:
        
        className = element.get_attribute('class')
        if ( className == 'C4VMK'):
            spanElement = element.find_element_by_tag_name('span')
            caption = HTMLParser().unescape(spanElement.text)
            break
    
    return caption, alt, img, srcset, sizes


def extract_posts(browser, num_of_posts_to_do, is_tag = False):
    """Get all posts from user"""
    links = []
    links2 = []
    srcsetPreview_imgs = {}
    sizesPreview_img = {}
    altPreview_img = {}
    srcPreview_img = {}

    errMsg = ''

    # list links contains 30 links from the current view, as that is the maximum Instagram is showing at one time
    # list links2 contains all the links collected so far
    # preview_imgs dictionary maps link in links2 to liknk's post's preview image src
    try:
        body_elem = browser.find_element_by_tag_name('body')

        # load_button = body_elem.find_element_by_xpath\
        #  ('//a[contains(@class, "_1cr2e _epyes")]')
        # body_elem.send_keys(Keys.END)
        # sleep(3)

        # load_button.click()

        previouslen = 0
        breaking = 0

        num_of_posts_to_scroll = 12 * math.ceil(num_of_posts_to_do / 12)
        print("Getting first", num_of_posts_to_scroll,
              "posts but check ", num_of_posts_to_do,
              " posts only, if you want to change this limit, change limit_amount value in crawl_profile.py\n")
        while (len(links2) < num_of_posts_to_do):
            links2 = []
            if is_tag:
                main = browser.find_element_by_tag_name('main')
                article_children = main.find_elements_by_xpath('./article/*')
                prev_divs = [article_children[2]]
            else:
                prev_divs = browser.find_elements_by_tag_name('main')
            links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]
            links = sum([[link_elem.get_attribute('href')
                for link_elem in elems] for elems in links_elems], [])
            for elems in links_elems:
                for link_elem in elems:
                    href = link_elem.get_attribute('href')
                    try:
                        img = link_elem.find_element_by_tag_name('img')
                    except NoSuchElementException:
                        continue
                    srcsetPreview_imgs[href] = img.get_attribute('srcset')
                    sizesPreview_img[href] = img.get_attribute('sizes')
                    altPreview_img[href] = img.get_attribute('alt')
                    srcPreview_img[href] = img.get_attribute('src')
            for link in links:
                if "/p/" in link:
                    if (len(links2) < num_of_posts_to_do):
                        links2.append(link)
            links2 = list(set(links2)) #remove duplicate elems
            print("Scrolling profile ", len(links2), "/", num_of_posts_to_scroll)
            body_elem.send_keys(Keys.END)
            sleep(Settings.sleep_time_between_post_scroll)

            ##remove bellow part to never break the scrolling script before reaching the num_of_posts
            if (len(links2) == previouslen):
                breaking += 1
                print("breaking in ", 4 - breaking,
                      "...\nIf you believe this is only caused by slow internet, increase sleep time 'sleep_time_between_post_scroll' in settings.py")
            else:
                breaking = 0
            if breaking > 3:
                print("\nNot getting any more posts, ending scrolling.")
                sleep(2)
                break
            previouslen = len(links2)
            ##

    except NoSuchElementException as err:
        print('- Something went terribly wrong\n')

    post_infos = []

    counter = 1

    for link in links2:
        print("\n", counter, "/", len(links2))
        
        counter = counter + 1

        print("\nScrapping link: ", link)
        web_adress_navigator(browser, link)
        try:
            caption, alt, img, srcset, sizes = extract_post_info(browser)

            post_infos.append({
                'url': link,
                'caption': caption,
                'src': img,
                'srcset': srcset,
                'sizes': sizes,
                'alt': alt,
                'srcSmall': srcPreview_img[link],
                'srcsetSmall': srcsetPreview_imgs[link],
                'sizesSmall': sizesPreview_img[link],
                'altSmall': altPreview_img[link],                
            })
            msg = ''
            if (caption == '' or caption == None): msg = msg + "caption is null,"
            if (alt == '' or alt == None): msg = msg + "alt is null,"
            if (img == '' or img == None): msg = msg + "img is null,"
            if (srcset == '' or img == None): msg = msg + "srcset is null,"
            if (msg != ''): errMsg = errMsg + '   - Link = ' + link + " : " + msg + '\n'
            print('msg = ' + msg)
        except NoSuchElementException as err:
            print('- Could not get information from post: ' + link)
            print(err)
            errMsg = errMsg + '- Could not get information from post: ' + link

    return post_infos, errMsg


def extract_information(browser, username, limit_amount):
    """Get all the information for the given username"""

    user_link = "https://www.instagram.com/{}/".format(username)
    web_adress_navigator(browser, user_link)
    prev_divs = browser.find_elements_by_class_name('_70iju')

    post_infos = []
    user_commented_total_list = []
    num_of_posts_to_do = 12
    errMsg = ''
    if Settings.scrap_posts_infos is True:
        try:
            post_infos, errMsg = extract_posts(browser, num_of_posts_to_do)
        except:
            pass

    information = {
        'scrapped': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'images': post_infos
    }

    return information, errMsg


def extract_tag_information(browser, tag, limit_amount):
    """Get all the information for the given tag"""

    tag_link = "https://www.instagram.com/explore/tags/{}/".format(tag)
    web_adress_navigator(browser, tag_link)
    num_of_posts_to_do = 12
    post_infos = []
    errMsg = ''
    if Settings.scrap_posts_infos is True:
        post_infos, errMsg = extract_posts(browser, num_of_posts_to_do, True)
    
    information = {
        'scrapped': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'images': post_infos
    }

    return information, errMsg