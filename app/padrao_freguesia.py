import logging
import requests
from bs4 import BeautifulSoup


headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.academiadasapostasbrasil.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.academiadasapostasbrasil.com/",
    # 'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    "x-requested-with": "XMLHttpRequest",
    #'Cookie': 'PHPSESSID=rastjvsj7rd5376v920cfentrh'
}


# Função para obter o timestamp de 21:00:00 de um dia específico
def get_timestamp_21h(date):
    # Cria uma data no formato desejado com as 21:00:00
    date_21h = date.replace(hour=21, minute=0, second=0, microsecond=0)
    return int(date_21h.timestamp())


def scrapy_matchs(starttime):
    """
    Get matchs list.

    Args:

        startime(_str_) -> timestamp

    Example:

        scrapy_matchs('1738627200') # GMT: Tuesday, 4 February 2025 00:00:00

    Returns:

        html(_str_) -> html with match of the day
    """
    url = "https://www.academiadasapostasbrasil.com/stats/livescores/widget/large"

    payload = f"starttime={starttime}&live=false&competitions_selected=&anydate=0&search_filter=&match_selected=null&my_matches=false&tab=%23fh_main_tab&competitions_has_changed=false&popup=false&show_blocked=false"
    # payload = f"starttime={starttime}&live=false&competitions_selected%5B%5D=88&competitions_selected%5B%5D=87&competitions_selected%5B%5D=1153&competitions_selected%5B%5D=156&competitions_selected%5B%5D=155&competitions_selected%5B%5D=950&competitions_selected%5B%5D=32&competitions_selected%5B%5D=15&competitions_selected%5B%5D=70&competitions_selected%5B%5D=8&competitions_selected%5B%5D=287&competitions_selected%5B%5D=2219&competitions_selected%5B%5D=98&competitions_selected%5B%5D=12&competitions_selected%5B%5D=7&competitions_selected%5B%5D=290&competitions_selected%5B%5D=945&competitions_selected%5B%5D=622&competitions_selected%5B%5D=11&competitions_selected%5B%5D=9&competitions_selected%5B%5D=101&competitions_selected%5B%5D=2229&competitions_selected%5B%5D=100&competitions_selected%5B%5D=63&competitions_selected%5B%5D=593&competitions_selected%5B%5D=392&competitions_selected%5B%5D=386&competitions_selected%5B%5D=389&competitions_selected%5B%5D=395&competitions_selected%5B%5D=390&competitions_selected%5B%5D=394&competitions_selected%5B%5D=387&competitions_selected%5B%5D=388&competitions_selected%5B%5D=240&competitions_selected%5B%5D=17&competitions_selected%5B%5D=16&competitions_selected%5B%5D=293&competitions_selected%5B%5D=14&competitions_selected%5B%5D=13&competitions_selected%5B%5D=438&competitions_selected%5B%5D=90&competitions_selected%5B%5D=158&competitions_selected%5B%5D=162&competitions_selected%5B%5D=52&competitions_selected%5B%5D=24&competitions_selected%5B%5D=549&competitions_selected%5B%5D=1&competitions_selected%5B%5D=97&competitions_selected%5B%5D=19&competitions_selected%5B%5D=125&competitions_selected%5B%5D=1133&competitions_selected%5B%5D=33&competitions_selected%5B%5D=373&competitions_selected%5B%5D=180&competitions_selected%5B%5D=91&competitions_selected%5B%5D=61&competitions_selected%5B%5D=75&competitions_selected%5B%5D=82&competitions_selected%5B%5D=111&competitions_selected%5B%5D=67&competitions_selected%5B%5D=200&competitions_selected%5B%5D=117&competitions_selected%5B%5D=157&competitions_selected%5B%5D=120&competitions_selected%5B%5D=119&competitions_selected%5B%5D=381&competitions_selected%5B%5D=122&competitions_selected%5B%5D=121&competitions_selected%5B%5D=46&competitions_selected%5B%5D=175&competitions_selected%5B%5D=45&competitions_selected%5B%5D=99&competitions_selected%5B%5D=27&competitions_selected%5B%5D=440&competitions_selected%5B%5D=85&competitions_selected%5B%5D=493&competitions_selected%5B%5D=370&competitions_selected%5B%5D=1910&competitions_selected%5B%5D=1908&competitions_selected%5B%5D=283&competitions_selected%5B%5D=50&competitions_selected%5B%5D=59&competitions_selected%5B%5D=118&competitions_selected%5B%5D=564&competitions_selected%5B%5D=1110&competitions_selected%5B%5D=136&competitions_selected%5B%5D=109&competitions_selected%5B%5D=110&competitions_selected%5B%5D=732&competitions_selected%5B%5D=113&competitions_selected%5B%5D=79&competitions_selected%5B%5D=143&competitions_selected%5B%5D=234&competitions_selected%5B%5D=64&competitions_selected%5B%5D=86&competitions_selected%5B%5D=74&competitions_selected%5B%5D=137&competitions_selected%5B%5D=152&competitions_selected%5B%5D=210&competitions_selected%5B%5D=153&competitions_selected%5B%5D=123&competitions_selected%5B%5D=106&competitions_selected%5B%5D=80&competitions_selected%5B%5D=78&competitions_selected%5B%5D=134&competitions_selected%5B%5D=215&competitions_selected%5B%5D=216&competitions_selected%5B%5D=163&competitions_selected%5B%5D=165&competitions_selected%5B%5D=205&competitions_selected%5B%5D=315&competitions_selected%5B%5D=320&competitions_selected%5B%5D=378&competitions_selected%5B%5D=150&competitions_selected%5B%5D=39&competitions_selected%5B%5D=179&competitions_selected%5B%5D=1038&anydate=&search_filter=&match_selected=null&my_matches=false&tab=%23fh_main_tab&competitions_has_changed=true&popup=false&show_blocked=false"

    response = requests.request("POST", url, headers=headers, data=payload, timeout=20)

    html = response.json()["html"]
    # with open(f'main_matchs_{starttime}.html', 'w') as file:
    #     file.write(html)

    return html


def fregues_recente(soup: BeautifulSoup) -> int | None:
    """
    Retorna time q não vence a 4 jogos

    Args:

        soup -> (__bs4.Beautifulsoup__)

    Returns:

        (__int__) -> 0 ou 1

        0 = "mandante"
        1 = "visitante"

    """
    # historico de confrontos
    h2h = soup.find("div", id="show_h2h")
    # Sem resultados nos últimos
    h2h = h2h.find("tbody").find_all("tr")
    historico_confrontos = []

    if len(h2h) <= 3:  # sem resultados suficientes para analise
        return None

    for hist in h2h:
        if hist == h2h[-1]:
            continue  # pular o último pois é o "Mostrar todos os jogos"

        hist_dict = {}
        tds = hist.find_all("td")
        hist_dict["data"] = (
            tds[0]
            .text.replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace(" ", "")
        )
        hist_dict["mandante"] = (
            tds[2]
            .text.replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace(" ", "")
        )
        hist_dict["placar"] = (
            tds[3]
            .text.replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace(" ", "")
        )
        hist_dict["visitante"] = (
            tds[4]
            .text.replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace(" ", "")
        )
        try:
            hist_dict["stat"] = tds[3].attrs["class"][
                0
            ]  # stat-lose = mandante perdeu, stat-win = mandante venceu e stat-draw empatou
        except:
            hist_dict["stat"] = None
        historico_confrontos.append(hist_dict)

    if len(historico_confrontos) >= 4:
        analise_stats = []
        for index, analise in enumerate(historico_confrontos):
            analise_stats.append(analise["stat"])
            if index >= 3:
                break

        if (
            "stat-win" in analise_stats and "stat-lose" not in analise_stats
        ):  # mandante nao perdeu ultimos 4 jogos
            logging.info("- Visitante é fregues a 4 jogos ou mais")
            return 1

        if (
            "stat-win" not in analise_stats and "stat-lose" in analise_stats
        ):  # visitante nao perdeu ultimos 4 jogos
            logging.info("- Mandante é fregues a 4 jogos ou mais")
            return 0

    else:
        logging.info("Quantidade de dados inválidos para identificação do padrão")


def nao_venceu_ultimos_4_jogos_casafora(soup: BeautifulSoup, fregues: int) -> bool:
    """
    Retorna padrão freguesia se time nao venceu 4+ ultimos jogos

    Args:

        soup -> (__bs4.Beautifulsoup__)

    Returns:

        (__bool__)

        Quando True -> padrão freguesia encontrado

        Quando False -> não é padrão

    """
    tables = soup.find_all("table")
    ultimos_jogos = None
    for table in tables:  # encontrar tabela com ultimos jogos do time na competição
        if "Todos os jogos na condição Casa/Fora" in table.text:
            ultimos_jogos = table

    if ultimos_jogos != None:
        # identificar ultimos 4 jogos da equipe q não vence na condição casa/fora
        ultimos_4_jogos = ultimos_jogos.find_all("table")[fregues]
        trs = ultimos_4_jogos.find("tbody").find_all("tr")

        if len(trs) <= 3:  # sem resultados suficientes para analise
            return None

        ultimos_confrontos = []
        for tr in trs:
            dict_helper = {}
            dict_helper["mandante"] = (
                tr.find_all("td")[1]
                .text.replace("\r", "")
                .replace("\n", "")
                .replace("\t", "")
                .replace(" ", "")
            )
            dict_helper["placar"] = (
                tr.find_all("td")[2]
                .text.replace("\r", "")
                .replace("\n", "")
                .replace("\t", "")
                .replace(" ", "")
            )
            dict_helper["adversario"] = (
                tr.find_all("td")[3]
                .text.replace("\r", "")
                .replace("\n", "")
                .replace("\t", "")
                .replace(" ", "")
            )
            stat = None
            for classe in tr.find_all("td")[2].attrs["class"]:
                if "stat-" in classe:
                    stat = classe
            dict_helper["stat"] = stat
            ultimos_confrontos.append(dict_helper)

        if len(ultimos_confrontos) >= 4:
            analise_stats = []
            for index, analise in enumerate(ultimos_confrontos):
                analise_stats.append(analise["stat"])
                if index >= 3:
                    break

            if "stat-win" not in analise_stats:
                # print('- Nao venceu nos ultimos 4 jogos ou mais na competição')
                # print('PADRÃO FREGUESIA!!')
                return True

    return False

