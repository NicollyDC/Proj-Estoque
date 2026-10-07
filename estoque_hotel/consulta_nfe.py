import base64

import requests


API_URL = "https://consultadanfe.com/api/v1/consulta"


def validar_chave(chave):
    chave = (chave or "").strip()

    if len(chave) != 44 or not chave.isdigit():
        raise ValueError(
            "A chave de acesso deve ter exatamente 44 números."
        )

    return chave


def consultar_nfe(chave):
    chave = validar_chave(chave)

    try:
        resposta = requests.post(
            API_URL,
            json={"chave": chave},
            timeout=30
        )
    except requests.Timeout:
        raise RuntimeError(
            "A consulta da NF-e demorou demais. Verifique a internet e tente novamente."
        )
    except requests.RequestException:
        raise RuntimeError(
            "Não foi possível consultar a NF-e. Verifique a conexão com a internet."
        )

    if resposta.status_code != 200:
        mensagem = "Não foi possível consultar esta NF-e no momento."

        try:
            erro = resposta.json()
            mensagem = (
                erro.get("mensagem")
                or erro.get("message")
                or mensagem
            )
        except Exception:
            pass

        raise RuntimeError(str(mensagem))

    try:
        dados = resposta.json()
    except Exception:
        raise RuntimeError(
            "Não foi possível ler a resposta da consulta da NF-e."
        )

    if dados.get("status") != "ok":
        raise RuntimeError(
            dados.get("mensagem") or "Não foi possível consultar a NF-e."
        )

    xml_base64 = dados.get("xml_base64")

    if not xml_base64:
        raise RuntimeError("A consulta não retornou os dados da NF-e.")

    try:
        xml_bytes = base64.b64decode(xml_base64)
    except Exception:
        raise RuntimeError("Os dados da NF-e recebidos estão incompletos.")

    if not xml_bytes:
        raise RuntimeError("A consulta retornou uma NF-e vazia.")

    return xml_bytes
