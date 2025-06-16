import logging

from datetime import date, datetime, timedelta

import requests
from bs4 import BeautifulSoup
from flask import Flask, flash, redirect, render_template, request
from sqlalchemy import select, desc

from app.db import PadraoFreguesia, Session, engine
from app.padrao_freguesia import (fregues_recente, get_timestamp_21h,
                                  nao_venceu_ultimos_4_jogos_casafora,
                                  scrapy_matchs)

import time
import json
from pathlib import Path
from threading import Lock


logging.basicConfig(
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s: %(message)s"
)

app = Flask(__name__)

app.secret_key = "os.getenv('SECRET_KEY')"
observacao_lock = Lock()

ARQUIVO_ANALISADAS = "urls_analisadas.json"
ARQUIVO_OBSERVACAO = "urls_observacao.json"

# Carregar do arquivo (caso exista)
if Path(ARQUIVO_ANALISADAS).exists():
    with open(ARQUIVO_ANALISADAS, "r") as f:
        urls_analisadas = json.load(f)
else:
    urls_analisadas = [] # para ignorar urls q já foram analisadas

if Path(ARQUIVO_OBSERVACAO).exists():
    with open(ARQUIVO_OBSERVACAO, "r") as f:
        lista_jogos_em_observacao = json.load(f)
else:
    lista_jogos_em_observacao = []



def filtrar_jogos_em_observacao() -> tuple:
    """
    Filtra jogos em observacao e ajuda montar os blocos da tela de admin

    Returns:
        
        Filtros (tuple): (filter_lista_jogos_em_observacao, lista_jogos_recomendados, ultimas_entradas)

    """
    # Ajuste da rota seção de observacao
    urls_observacao = []
    for jogo in lista_jogos_em_observacao:
        urls_observacao.append(jogo["url"])

    with Session(engine) as session:
        stmt_urls = select(PadraoFreguesia.url).filter(
            PadraoFreguesia.url.in_(urls_observacao)
        )
        urls_do_banco = session.scalars(stmt_urls).all()

        # Aproveita e faz select da seção de recomendadas
        stmt_ultimas_entradas = select(PadraoFreguesia).filter(
            PadraoFreguesia.resultado == None
        )
        lista_jogos_recomendados = session.scalars(stmt_ultimas_entradas).all()

        # Aproveita e faz select da seção de ultimas entradas
        stmt_ultimas_entradas = (
            select(PadraoFreguesia)
            .filter(PadraoFreguesia.resultado != None)
            .order_by(desc(PadraoFreguesia.data_partida)).limit(30)
        )
        ultimas_entradas = session.scalars(stmt_ultimas_entradas).all()

    # filtra entradas em observacao
    filter_lista_jogos_em_observacao = []
    for jogo in lista_jogos_em_observacao:
        if jogo["url"] not in urls_do_banco:
            filter_lista_jogos_em_observacao.append(jogo)

    return filter_lista_jogos_em_observacao, lista_jogos_recomendados, ultimas_entradas


@app.route("/vars")
def appvars():
    return {"urls_analisadas": urls_analisadas, "lista_obs": lista_jogos_em_observacao}


@app.route("/")
@app.route("/freguesia")
def freguesia():
    """Tela inicial."""
    filter_lista_jogos_em_observacao, lista_jogos_recomendados, ultimas_entradas = (
        filtrar_jogos_em_observacao()
    )
    return render_template(
        "admin_content.html",
        lista_jogos_em_observacao=filter_lista_jogos_em_observacao,
        lista_jogos_recomendados=lista_jogos_recomendados,
        ultimas_entradas=ultimas_entradas
    )


@app.route("/recomendar-entrada/", defaults={"id": None})
@app.route("/recomendar-entrada/<id>")
def recomendar_entrada(id):
    """preencher input de odds antes de recomendar"""
    # se o id existe na lista vamos prosseguir
    for jogo in lista_jogos_em_observacao:
        if id == jogo["id"]:
            # exbir formulário para input de odds, url e envio
            return render_template(
                "form_recomendar.html",
                jogo=jogo,
            )

    # caso nao encontre o ID não faz nada
    return redirect("/freguesia")


@app.post("/enviar-entrada")
def enviar_entrada():
    print(request.form)

    for jogo in lista_jogos_em_observacao:
        if jogo["id"] == request.form.get("event_id"):
            url = jogo["url"]
            fregues = jogo["fregues"]
            campeonato = url.split("/")[-5] + "/" + url.split("/")[-4]
            mandante = url.split("/")[-3]
            visitante = url.split("/")[-2]

            print("processando...")
            print(locals())
            with Session(engine) as session:
                evento = PadraoFreguesia(
                    data_partida=datetime.strptime(jogo["data_partida"], "%Y-%m-%d").date(),
                    url=url,
                    fregues=fregues,
                    campeonato=campeonato,
                    mandante=mandante,
                    visitante=visitante,
                    odd_mandante=request.form.get("odd_mandante"),
                    odd_visitante=request.form.get("odd_visitante"),
                )
                session.add(evento)
                try:
                    session.commit()
                except Exception as error:
                    logging.error("ERRO ao enviar entrada: %s", str(error))
                    pass
            break

    return redirect("/freguesia")


@app.route("/jogos-observacao", methods=["GET", "POST"])
def jogos_em_observacao():
    """Carrega e retorna jogos em observação"""
    if not observacao_lock.acquire(blocking=False):
        return "Aguarde! Processo em andamento..."

    try:
        for i in range(1, -2, -1):   # 1 = hoje | 0 = amanha | -1 = dps_de_amanha
            hoje = datetime.now() - timedelta(
                days=i
            )  # é normal contar como o dia atual para gerar o timestamp
            stamp = get_timestamp_21h(hoje)
            hoje += timedelta(days=1)
            logging.info("----- Dia: %s -----", hoje.date())

            html = scrapy_matchs(stamp)
            soup = BeautifulSoup(html, "html.parser")
            main_matchs = soup.find_all(
                "tr", class_="live-subscription"
            )  # Armazena todos os jogos
            logging.info("Quantidade de jogos para analise: %s ", len(main_matchs))

            for match in main_matchs:
                match_dict = {}
                match_dict["data_partida"] = (
                    hoje.date().strftime("%Y-%m-%d")
                )  # match.find('td', class_='hour').text.replace('\t', ' ').replace(' ', '').split('\n')[-1]
                match = match.find("td", class_="score")
                match_url = match.find("a")["href"]

                if match_url in urls_analisadas:
                    continue

                response = requests.get(match_url)
                if response.status_code == 200:
                    urls_analisadas.append(match_url)

                    soup = BeautifulSoup(response.text, "html.parser")

                    fregues = fregues_recente(soup)

                    if fregues != None:
                        dp = nao_venceu_ultimos_4_jogos_casafora(soup, fregues)

                        if dp:
                            logging.warning("FREGUESIA: %s", match_url)
                            match_dict["url"] = match_url
                            match_dict["fregues"] = None
                            match_dict['id'] = match_url.split('/')[-1]

                            match_dict["mandante"] = match_url.split('/')[-3]
                            match_dict["visitante"] = match_url.split('/')[-2]

                            match_dict["evento"] = f'{hoje.day}.{hoje.month} - {match_dict["mandante"]} v {match_dict["visitante"]}'

                            if fregues == 0:
                                match_dict["fregues"] = "mandante"
                                match_dict["entrada_alias"] = f'A favor do VISITANTE: {match_dict["visitante"]}'

                            if fregues == 1:
                                match_dict["fregues"] = "visitante"
                                match_dict["entrada_alias"] = f'A favor do MANDANTE: {match_dict["mandante"]}'

                            lista_jogos_em_observacao.append(match_dict)


            logging.info('Salvando arquivos json...')
            while len(urls_analisadas) > 200: # limpa urls antigas
                urls_analisadas.pop(0) # vai removendo o primeiro item até atender condicao
                
            with open(ARQUIVO_ANALISADAS, "w") as f:
                json.dump(urls_analisadas, f, indent=2)

            with open(ARQUIVO_OBSERVACAO, "w") as f:
                json.dump(lista_jogos_em_observacao, f, indent=2)

        filter_lista_jogos_em_observacao, _, _ = filtrar_jogos_em_observacao()
        return filter_lista_jogos_em_observacao
    
    finally:
        observacao_lock.release() # libera o processo


@app.route("/atualizar-entradas", methods=["GET", "POST"])
def atualizar_entradas():
    """
    Atualiza entradas que estão em aberto no banco...
    """
    time.sleep(1)
    stmt = select(PadraoFreguesia).filter(PadraoFreguesia.placar == None)
    with Session(engine) as session:
        entradas_recomendadas = session.scalars(stmt).all()
        # aqui temos todos objetos ORM de entradas em andamento

    # atualizar o placar dos jogos do banco
    commit_db = False  # se vai precisar fazer a alteração no banco
    for index, entrada in enumerate(entradas_recomendadas):
        # print(entrada.url)
        try:
            response = requests.get(entrada.url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            match_head_score = soup.find("ul", class_="match-head-score").text
            # print(match_head_score)
        except:
            continue

        if "Terminado" in match_head_score:
            placar = (
                soup.find("ul", class_="match-head-score")
                .find_all("li")[0]
                .text.replace("\r", "")
                .replace("\n", "")
                .replace("\t", "")
                .replace(" ", "")
            )

            # tenta atualizar resultado
            try:
                if len(placar.split("-")) == 2:
                    casa = int(placar.split("-")[0])
                    fora = int(placar.split("-")[1])

                    if casa == fora:
                        resultado = "red"

                    elif casa > fora:
                        if entrada.fregues.name == "visitante":
                            resultado = "green"
                        else:
                            resultado = "red"

                    elif fora > casa:
                        if entrada.fregues.name == "mandante":
                            resultado = "green"
                        else:
                            resultado = "red"

                    commit_db = True
                    entradas_recomendadas[index].resultado = resultado
                    entradas_recomendadas[index].placar = placar
                    
                    # se o jogo está sendo atualizado, remove da lista de observacao
                    for obs_jogo in lista_jogos_em_observacao:
                        if obs_jogo["url"] == entrada.url: 
                            lista_jogos_em_observacao.remove(obs_jogo)

            except Exception as error:
                logging.error("Falha ao atualizar o placar: %s", error)

    entradas_recomendadas_final = entradas_recomendadas
    if commit_db:
        with Session(engine) as session:
            session.add_all(entradas_recomendadas)
            session.commit()
            entradas_recomendadas_final = session.scalars(stmt).all()

    qt_entradas = len(entradas_recomendadas) - len(entradas_recomendadas_final)

    if qt_entradas > 0:
        flash(f"{qt_entradas} jogo(s) atualizado(s).", "rec_success")
    else:
        flash(f"Nenhum jogo atualizado no momento...", "rec_error")

    return redirect("/freguesia")


@app.route("/remover-observacao/<id>")
def remover_observacao(id):
    for jogo in lista_jogos_em_observacao:
        if jogo["id"] == id:
            lista_jogos_em_observacao.remove(jogo)
            urls_analisadas.remove(jogo["url"])
            
            # mandar flash e atualizar jsons
            flash("Jogo removido com sucesso!", "obs_success")

            with open(ARQUIVO_ANALISADAS, "w") as f:
                json.dump(urls_analisadas, f, indent=2)

            with open(ARQUIVO_OBSERVACAO, "w") as f:
                json.dump(lista_jogos_em_observacao, f, indent=2)

            return redirect("/freguesia")


