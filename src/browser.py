from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from env import settings

def init_browser():
  options = Options()
  for argument in settings.chromium_arguments:
    options.add_argument(argument)
  options.binary_location = settings.chromium_path

  driver = webdriver.Chrome(options=options)

  return driver

def find_element(driver, by, value):
  try:
    element = driver.find_element(by, value)
    return element
  except NoSuchElementException:
    return None

@contextmanager
def browser():
  driver = init_browser()
  try:
    yield driver
  finally:
    driver.quit()