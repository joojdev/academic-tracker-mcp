from server import mcp
from env import settings
from selenium.webdriver.common.by import By

def main():
  if settings.dev_mode:
    mcp.run()
  else:
    mcp.run(transport='http', host='127.0.0.1', port=settings.mcp_server_port)

if __name__ == '__main__':
  main()