from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from env import settings

_driver = None
_logged_in = False

def get_session():
  global _driver, _logged_in
  if _driver is None:
    _driver = init_browser()
  if not _logged_in:
    from webscraping import login_routine
    for attempt in range(3):
      if login_routine(_driver):
        _logged_in = True
        break
      if attempt == 2:
        raise RuntimeError('Login falhou 3 vezes seguidas')
  return _driver

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