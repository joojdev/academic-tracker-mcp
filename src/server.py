from fastmcp import FastMCP
from browser import get_session
from webscraping import get_periods, get_grades, get_grade_details
from env import settings

mcp = FastMCP("Academic Tracker MCP")

@mcp.tool
def list_possible_periods():
  """Lista os períodos letivos disponíveis no boletim do aluno.

  Use esta ferramenta primeiro para descobrir quais períodos existem antes de
  consultar notas. O campo `value` de cada item é o identificador que deve ser
  passado como parâmetro `period` nas outras ferramentas.

  Retorna uma lista de objetos com os campos:
  - value (str): identificador do período no formato "AAAA/N" (ex: "2024/1")
  - label (str): rótulo legível exibido na interface (ex: "2024/1 - 1º Semestre")
  """
  driver = get_session()
  periods = get_periods(driver, settings.suap_id)
  return periods

@mcp.tool
def get_grades_from_period(period: str):
  """Retorna o boletim resumido de todas as disciplinas de um período letivo.

  Use `list_possible_periods` para obter os valores válidos de `period`.
  Prefira esta ferramenta quando quiser uma visão geral rápida de todas as
  disciplinas sem precisar do detalhamento de cada avaliação.

  Parâmetros:
  - period (str): identificador do período no formato "AAAA/N" (ex: "2024/1")

  Retorna uma lista de objetos, um por disciplina, com os campos:
  - disciplina (str): nome completo da disciplina
  - total_faltas (str): total de faltas acumuladas no período
  - frequencia (str): percentual de frequência (ex: "85.0%")
  - situacao (str): situação atual do aluno na disciplina (ex: "Cursando", "Aprovado")
  - n1 (object): nota e faltas da primeira etapa
    - nota (str): nota obtida na etapa (vazio se ainda não lançada)
    - faltas (str): faltas registradas na etapa
  - media (str): média parcial ou final calculada
  - naf (object): nota e faltas da avaliação final (NAF), quando aplicável
    - nota (str): nota obtida na NAF
    - faltas (str): faltas registradas na NAF
  - mfd (str): média final da disciplina após NAF, quando aplicável
  """
  driver = get_session()
  data = get_grades(driver, settings.suap_id, period)
  return data

@mcp.tool
def get_full_grades_from_period(period: str):
  """Retorna o boletim completo de todas as disciplinas de um período letivo,
  incluindo a lista de professores e o detalhamento de cada avaliação por etapa.

  Use esta ferramenta quando precisar saber quais provas/trabalhos compõem a
  nota de uma disciplina, os pesos de cada avaliação, ou quem é o professor
  responsável. É mais lenta que `get_grades_from_period` pois acessa a página
  de detalhes de cada disciplina individualmente.

  Use `list_possible_periods` para obter os valores válidos de `period`.

  Parâmetros:
  - period (str): identificador do período no formato "AAAA/N" (ex: "2024/1")

  Retorna uma lista de objetos, um por disciplina, com todos os campos de
  `get_grades_from_period` (exceto `detalhar_url`) mais:
  - professores (list[str]): nomes dos professores responsáveis pela disciplina
  - etapas (list[object]): etapas de avaliação da disciplina, cada uma com:
    - etapa (str): nome da etapa (ex: "1ª Etapa", "Avaliação Final")
    - avaliacoes (list[object]): avaliações realizadas na etapa, cada uma com:
      - sigla (str): sigla da avaliação (ex: "P1", "T1")
      - tipo (str): tipo de avaliação (ex: "Prova", "Trabalho")
      - descricao (str): descrição detalhada da avaliação
      - data (str): data de realização no formato "DD/MM/AAAA"
      - peso (str): peso da avaliação no cálculo da média
      - nota_obtida (str): nota obtida pelo aluno (vazio se não lançada)
  """
  driver = get_session()
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