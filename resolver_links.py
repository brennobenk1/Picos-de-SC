#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resolver_links.py  --  preenche as coordenadas dos links pendentes do mapa.html

Como usar:
    1. Deixe este arquivo na MESMA pasta do mapa.html
    2. Abra o terminal nessa pasta e rode:   python3 resolver_links.py
    3. Abra o mapa.html de novo. Os pins vão estar lá.

Ele segue cada link curto do Google Maps, pega o nome do lugar e as
coordenadas, e reescreve só o bloco entre INÍCIO DOS SAVES e FIM DOS SAVES.
Uma cópia de seguranca e gravada como mapa.html.bak antes de qualquer mudança.

Nao precisa instalar nada: usa so a biblioteca padrao do Python 3.
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapa.html")
INICIO = "const LUGARES = ["
FIM = "];"
PAUSA = 1.5          # segundos entre um link e outro
TENTATIVAS = 3
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def url_final(link):
    """Segue os redirecionamentos e devolve o endereco longo do Google Maps."""
    req = urllib.request.Request(link, headers={"User-Agent": UA,
                                                "Accept-Language": "pt-BR,pt;q=0.9"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.geturl()


ALFABETO_PLUS = "23456789CFGHJMPQRVWX"


def decodifica_plus(codigo):
    """Decodifica um Plus Code COMPLETO (ex. 584H542H+W5). Curto devolve None."""
    limpo = codigo.replace("+", "").upper()
    if len(limpo) < 8 or any(c not in ALFABETO_PLUS for c in limpo):
        return None
    lat = lng = 0.0
    pares = len(limpo) // 2
    for i in range(pares):
        d = 20.0 / (20 ** i)
        lat += ALFABETO_PLUS.index(limpo[2 * i]) * d
        lng += ALFABETO_PLUS.index(limpo[2 * i + 1]) * d
    meio = (20.0 / (20 ** (pares - 1))) / 2
    return lat - 90 + meio, lng - 180 + meio


def ler(url):
    """Tira nome e coordenadas de um endereco longo do Google Maps."""
    lat = lng = None
    nome = ""
    for padrao in (r"!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)",
                   r"[?&]q=(-?\d+(?:\.\d+)?),\+?(-?\d+(?:\.\d+)?)",
                   r"/maps/search/(-?\d+(?:\.\d+)?),\+?(-?\d+(?:\.\d+)?)",
                   r"/maps/place/(-?\d+(?:\.\d+)?),\+?(-?\d+(?:\.\d+)?)",
                   r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)"):
        m = re.search(padrao, url)
        if m:
            lat, lng = float(m.group(1)), float(m.group(2))
            break
    m = re.search(r"/maps/place/([^/@?]+)", url)
    if m:
        # Depois do unquote, o "+" pode ser espaco OU parte de um Plus Code.
        cru = urllib.parse.unquote(m.group(1))
        pc = re.match(r"([" + ALFABETO_PLUS + r"]{4,8}\+[" + ALFABETO_PLUS + r"]{2,3})(\+|$)", cru)
        resto = cru[pc.end(1):] if pc else cru
        texto = resto.replace("+", " ").strip().lstrip(",").strip()
        partes = [p.strip() for p in texto.split(",")]
        if not re.match(r"^-?\d+\.\d+$", partes[0]):
            nome = partes[0]
        if lat is None and pc:
            coord = decodifica_plus(pc.group(1))
            if coord:
                lat, lng = coord
            else:
                onde = partes[1] if len(partes) > 1 else "local desconhecido"
                print("      Plus Code curto (%s, perto de %s) - resolva na mao."
                      % (pc.group(1), onde))
    return nome, lat, lng


def tipo_por_nome(n):
    s = (n or "").lower()
    for padrao, tipo in (
        (r"cachoeir|cascata|queda|salto|v[ée]u de noiva", "cachoeira"),
        (r"gruta|caverna|furna|toca", "gruta"),
        (r"c[âa]nion|canyon", "canion"),
        (r"represa|barragem|lago|lagoa|a[çc]ude", "represa"),
        (r"praia|ponta|costa|enseada|ilha", "praia"),
        (r"mirante|vista panor", "mirante"),
        (r"trilha|parque|caminho|trekking", "trilha"),
        (r"morro|pico|monte|serra|pedra|cume", "morro"),
        (r"camping|acamp", "camping"),
    ):
        if re.search(padrao, s):
            return tipo
    return "ponto"


def campo(linha, nome):
    """Le um campo do registro JS, aceitando aspas ou null."""
    m = re.search(nome + r'\s*:\s*("(?:[^"\\]|\\.)*"|null|-?\d+(?:\.\d+)?)', linha)
    if not m:
        return None
    bruto = m.group(1)
    if bruto == "null":
        return None
    if bruto.startswith('"'):
        return json.loads(bruto)
    return float(bruto)


def main():
    if not os.path.exists(ARQUIVO):
        sys.exit("Nao achei o mapa.html nesta pasta. Deixe os dois arquivos juntos.")

    texto = open(ARQUIVO, encoding="utf-8").read()
    i = texto.find(INICIO)
    if i < 0:
        sys.exit("Nao achei o bloco 'const LUGARES = [' no mapa.html.")
    j = texto.find("\n];", i)
    if j < 0:
        sys.exit("Nao achei o fim do bloco dos saves.")
    bloco = texto[i:j + 3]

    linhas = [l for l in bloco.split("\n") if l.strip().startswith("{id:")]
    print("Encontrei %d lugares no arquivo." % len(linhas))

    pendentes = []
    for n, linha in enumerate(linhas):
        if campo(linha, "lat") is None and "maps.app.goo.gl" in linha:
            pendentes.append(n)
    print("Pendentes para resolver: %d\n" % len(pendentes))
    if not pendentes:
        print("Nada a fazer. Todos ja tem coordenada.")
        return

    resolvidos = 0
    falhas = []
    for contador, n in enumerate(pendentes, 1):
        linha = linhas[n]
        ident = campo(linha, "id") or "?"
        link = campo(linha, "link") or ""
        nome_atual = campo(linha, "nome") or ""
        rotulo = "[%d/%d] %s" % (contador, len(pendentes), ident)

        nome = lat = lng = None
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                nome, lat, lng = ler(url_final(link))
                break
            except Exception as erro:
                if tentativa == TENTATIVAS:
                    print("%s  FALHOU: %s" % (rotulo, erro))
                    falhas.append((ident, link))
                else:
                    time.sleep(3 * tentativa)

        if lat is None:
            if nome and not nome_atual:
                linhas[n] = re.sub(r'nome\s*:\s*("(?:[^"\\]|\\.)*"|null)',
                                   "nome:" + json.dumps(nome, ensure_ascii=False), linha, count=1)
                print("%s  so o nome: %s (sem coordenada)" % (rotulo, nome))
            elif (ident, link) not in falhas:
                print("%s  sem coordenada no link" % rotulo)
                falhas.append((ident, link))
        else:
            nome_final = nome_atual or nome or ""
            nova = linha
            nova = re.sub(r'nome\s*:\s*("(?:[^"\\]|\\.)*"|null)',
                          "nome:" + json.dumps(nome_final, ensure_ascii=False), nova, count=1)
            nova = re.sub(r"lat\s*:\s*(null|-?\d+(?:\.\d+)?)", "lat:%.7f" % lat, nova, count=1)
            nova = re.sub(r"lng\s*:\s*(null|-?\d+(?:\.\d+)?)", "lng:%.7f" % lng, nova, count=1)
            nova = re.sub(r'tipo\s*:\s*"[^"]*"', 'tipo:"%s"' % tipo_por_nome(nome_final), nova, count=1)
            linhas[n] = nova
            resolvidos += 1
            print("%s  %-42s %.6f, %.6f" % (rotulo, nome_final or "(sem nome)", lat, lng))

        time.sleep(PAUSA)

    novo_bloco = INICIO + "\n" + "\n".join(linhas) + "\n];"

    open(ARQUIVO + ".bak", "w", encoding="utf-8").write(texto)
    open(ARQUIVO, "w", encoding="utf-8").write(texto[:i] + novo_bloco + texto[j + 3:])

    print("\n--------------------------------------------")
    print("Resolvidos agora: %d" % resolvidos)
    if falhas:
        print("Nao resolvidos (%d):" % len(falhas))
        for ident, link in falhas:
            print("   %s  %s" % (ident, link))
        print("Rode de novo mais tarde, ou abra esses links na mao")
        print("e cole o endereco completo na aba Pendentes do site.")
    print("Backup salvo em mapa.html.bak")
    print("Abra o mapa.html para ver.")


if __name__ == "__main__":
    main()
