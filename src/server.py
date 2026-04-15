from fastmcp import FastMCP
from browser import browser
from webscraping import login_routine, get_periods, get_grades, get_grade_details
from env import settings

mcp = FastMCP("Academic Tracker MCP")

@mcp.tool
def list_possible_periods():
  """Retorna períodos disponíveis na conta do aluno"""
  with browser() as driver:
    logged = login_routine(driver)

    if not logged:
      raise RuntimeError('Login failed!')

    periods = get_periods(driver, settings.suap_id)

    return periods

@mcp.tool
def get_grades_from_period(period: str):
  """Retorna notas e faltas resumidas de cada disciplina no período."""
  with browser() as driver:
    logged = login_routine(driver)

    if not logged:
      raise RuntimeError('Login failed!')

    data = get_grades(driver, settings.suap_id, period)

    return data

@mcp.tool
def get_full_grades_from_period(period: str):
  """Retorna notas completas do período, incluindo o detalhamento de cada avaliação
  (provas, trabalhos, exercícios) e professores de cada disciplina."""
  with browser() as driver:
    logged = login_routine(driver)

    if not logged:
      raise RuntimeError('Login failed!')

    grades = get_grades(driver, settings.suap_id, period)

    if not grades:
      return grades

    for grade in grades:
      url = grade.pop('detalhar_url', None)
      if url:
        details = get_grade_details(driver, url)
        if details:
          grade['professores'] = details['professores']
          grade['etapas'] = details['etapas']

    return grades