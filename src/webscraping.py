from browser import find_element
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from env import settings

def login_routine(driver):
  # Ir para página inicial.
  driver.get('https://suap.ifsp.edu.br')

  # Procurar campos de login e senha e botão de enviar formulário.
  username_input = find_element(driver, By.ID, 'id_username')
  password_input = find_element(driver, By.ID, 'id_password')
  submit_button = find_element(driver, By.CSS_SELECTOR, '#login > form > .submit-row > input[type=submit]')

  if not username_input or not password_input or not submit_button:
    return False

  # Preencher campos de login e senha.
  username_input.send_keys(settings.suap_id)
  password_input.send_keys(settings.suap_password)

  # Apertar botão de enviar formulário.
  submit_button.click()

  # Verificar se o login teve sucesso ou não. Sucesso -> true. Falha -> false.
  # Elemento de erro: ".errornote"
  try:
    WebDriverWait(driver, 30).until(
      EC.any_of(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.errornote')),
        EC.presence_of_element_located((By.ID, 'user-tools'))
      )
    )
    loaded_next_page = True
  except TimeoutException:
    loaded_next_page = False

  if not loaded_next_page: return False

  login_success = find_element(driver, By.CSS_SELECTOR, '.errornote') == None

  return login_success

def get_periods(driver, id):
  # Ir para a página de boletim
  driver.get(f'https://suap.ifsp.edu.br/edu/aluno/{id}/?tab=boletim')

  # Esperar períodos
  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, '#ano_periodo'))
    )
  except TimeoutException:
    return []

  # Listar períodos
  select = find_element(driver, By.CSS_SELECTOR, '#ano_periodo')
  options = select.find_elements(By.TAG_NAME, 'option')
  result = [{'value': option.get_attribute('value'), 'label': option.text.strip()} for option in options]

  # Retornar períodos
  return result

def get_grades(driver, id, period_value):
  period_value = period_value.replace('/', '_')

  # Ir para a página de boletim
  driver.get(f'https://suap.ifsp.edu.br/edu/aluno/{id}/?tab=boletim')

  # Aguardar seletor de períodos E suas opções estarem disponíveis
  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, '#ano_periodo option'))
    )
  except TimeoutException:
    return None

  select_element = find_element(driver, By.CSS_SELECTOR, '#ano_periodo')
  if not select_element: return None

  # Capturar linha existente para detectar quando o reload terminar
  existing_rows = driver.find_elements(By.CSS_SELECTOR, '#tabela_boletim tbody tr')
  first_row = existing_rows[0] if existing_rows else None

  # Selecionar período via JS e disparar evento change para o HTMX processar o AJAX
  # bubbles: true é necessário para o HTMX capturar o evento
  driver.execute_script("""
    var sel = arguments[0];
    sel.value = arguments[1];
    sel.dispatchEvent(new Event('change', { bubbles: true }));
  """, select_element, period_value)

  # Aguardar linha antiga ficar stale (confirma que o AJAX recarregou a tabela)
  try:
    if first_row:
      WebDriverWait(driver, 10).until(EC.staleness_of(first_row))
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, '#tabela_boletim tbody tr'))
    )
  except TimeoutException:
    return None

  # Extrair notas e faltas
  rows = driver.find_elements(By.CSS_SELECTOR, '#tabela_boletim tbody tr')

  grades = []
  for row in rows:
    cells = row.find_elements(By.TAG_NAME, 'td')
    if len(cells) < 14:
      continue

    discipline = ' '.join(cells[1].text.split())

    detalhar_url = None
    if len(cells) >= 15:
      links = cells[14].find_elements(By.TAG_NAME, 'a')
      if links:
        detalhar_url = links[0].get_attribute('href')

    grades.append({
      'disciplina': discipline,
      'total_faltas': cells[5].text.strip(),
      'frequencia': cells[6].text.strip(),
      'situacao': cells[7].text.strip(),
      'n1': {
        'nota': cells[8].text.strip(),
        'faltas': cells[9].text.strip(),
      },
      'media': cells[10].text.strip(),
      'naf': {
        'nota': cells[11].text.strip(),
        'faltas': cells[12].text.strip(),
      },
      'mfd': cells[13].text.strip(),
      'detalhar_url': detalhar_url,
    })

  # Retornar dados
  return grades


def get_grade_details(driver, detalhar_url):
  driver.get(detalhar_url)

  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, 'h2'))
    )
  except TimeoutException:
    return None

  result = {
    'professores': [],
    'etapas': [],
  }

  # Extrair professores
  # Usa contains(.) em vez de contains(text()) pois o h3 tem ícone antes do texto
  prof_container = find_element(driver, By.XPATH, "//h3[contains(.,'Professores')]/following-sibling::div[1]")
  if prof_container:
    result['professores'] = [p.strip() for p in prof_container.text.split('\n') if p.strip()]

  # Extrair etapas e avaliações
  etapa_headings = driver.find_elements(By.CSS_SELECTOR, 'h4')
  for heading in etapa_headings:
    etapa_data = {
      'etapa': heading.text.strip(),
      'avaliacoes': [],
    }
    try:
      table = heading.find_element(By.XPATH, './following-sibling::table[1]')
      detail_rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')
      for detail_row in detail_rows:
        cells = detail_row.find_elements(By.TAG_NAME, 'td')
        if len(cells) >= 6:
          etapa_data['avaliacoes'].append({
            'sigla': cells[0].text.strip(),
            'tipo': cells[1].text.strip(),
            'descricao': cells[2].text.strip(),
            'data': cells[3].text.strip(),
            'peso': cells[4].text.strip(),
            'nota_obtida': cells[5].text.strip(),
          })
    except Exception:
      pass
    result['etapas'].append(etapa_data)

  return result