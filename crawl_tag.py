#!/usr/bin/env python3.5

"""Goes through all usernames and collects their information"""
import json
import datetime

from util.cli_helper import get_all_user_names
from util.settings import Settings
from util.datasaver import Datasaver

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from util.extractor import extract_information, extract_tag_information

chrome_options = Options()
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--lang=en-US')
chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})
browser = webdriver.Chrome('./assets/chromedriver', chrome_options=chrome_options)

# makes sure slower connections work as well        
print ("Waiting 10 sec")
browser.implicitly_wait(10)

try:
  tags = get_all_user_names()

  for tag in tags:
    print('Extracting information from #' + tag)
    information, user_commented_list = extract_tag_information(browser, tag, Settings.limit_amount)
    Datasaver.save_profile_json(tag,information)

    print ("Number of users who commented on his/her profile is ", len(user_commented_list),"\n")

    Datasaver.save_profile_commenters_txt(tag,user_commented_list)
    print ("\nFinished. The json file and nicknames of users who commented were saved in profiles directory.\n")

except KeyboardInterrupt:
  print('Aborted...')
except:
  pass
finally:
  browser.delete_all_cookies()
  browser.close()
  browser.quit()
