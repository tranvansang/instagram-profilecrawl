#!/usr/bin/env python3.5

"""Goes through all usernames and collects their information"""
import json
import datetime
import requests

from util.cli_helper import get_all_user_names
from util.settings import Settings
from util.datasaver import Datasaver

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from util.extractor import extract_information, extract_tag_information

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--kiosk")
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--lang=en-US')
chrome_options.add_argument('--headless')
chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US'})
browser = webdriver.Chrome('./assets/chromedriver', chrome_options=chrome_options)

# makes sure slower connections work as well        

try:
  tags = get_all_user_names()

  for tag in tags:
    print('Extracting information from #' + tag)
    information, errMsg = extract_tag_information(browser, tag, Settings.limit_amount)
    Datasaver.save_profile_json(tag,information)
    
    if (errMsg != '' and errMsg != None):
      #Send msg to slack
      webhook_url = 'https://hooks.slack.com/services/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'
      slack_data = {'text': '#InstagramCrawl:\n' + errMsg}

      response = requests.post(
          webhook_url, data=json.dumps(slack_data),
          headers={'Content-Type': 'application/json'}
      )
      if response.status_code != 200:
          raise ValueError(
              'Request to slack returned an error %s, the response is:\n%s'
              % (response.status_code, response.text)
          )
    print ("Number of users who commented on his/her profile is ", len(user_commented_list),"\n")

except KeyboardInterrupt:
  print('Aborted...')
except:
  pass
finally:
  browser.delete_all_cookies()
  browser.close()
  browser.quit()
