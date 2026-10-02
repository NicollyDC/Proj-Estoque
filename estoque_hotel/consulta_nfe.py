import base64
import requests


API_URL = "https://consultadanfe.com/api/v1/consulta"


def validar_chave(chave):
    """
    Valida se a chave possui exatamente 44 dígitos.
    """

    chave = chave.strip()

    if len(chave) != 44:
        raise ValueError(
            "A chave de acesso deve ter exatamente 44 dígitos."
        )

    if not chave.isdigit():
        raise ValueError(
            "A chave de acesso deve conter apenas números."
        )

    return chave


def consultar_nfe(chave):
    """
    Consulta uma NF-e pela chave
    e retorna o XML em bytes.

    O XML permanece apenas em memória.
    """

    chave = validar_chave(chave)

    resposta = requests.post(
        API_URL,
        json={
            "chave": chave
        },
        timeout=30
    )

    if resposta.status_code != 200:

        try:
            erro = resposta.json()

            mensagem = (
                erro.get("mensagem")
                or erro.get("message")
                or erro
            )

        except Exception:
            mensagem = resposta.text

        raise Exception(
            f"Erro da API ({resposta.status_code}): {mensagem}"
        )

    try:
        dados = resposta.json()

    except Exception:
        raise Exception(
            "A API retornou uma resposta inválida."
        )

    if dados.get("status") != "ok":
        raise Exception(
            dados.get(
                "mensagem",
                "Não foi possível consultar a NF-e."
            )
        )

    xml_base64 = dados.get(
        "xml_base64"
    )

    if not xml_base64:
        raise Exception(
            "A API não retornou o XML da NF-e."
        )

    try:
        xml_bytes = base64.b64decode(
            xml_base64
        )

    except Exception as e:
        raise Exception(
            f"Não foi possível decodificar o XML: {e}"
        )

    if not xml_bytes:
        raise Exception(
            "A API retornou um XML vazio."
        )

    return xml_bytes


if __name__ == "__main__":

    chave = input(
        "Digite a chave de acesso da NF-e: "
    ).strip()

    try:
        xml = consultar_nfe(chave)

        print(
            "NF-e consultada com sucesso!"
        )

        print(
            f"Tamanho do XML recebido: {len(xml)} bytes"
        )

        print(
            "O XML não foi salvo em arquivo."
        )

    except Exception as e:

        print(
            f"Erro: {e}"
        )