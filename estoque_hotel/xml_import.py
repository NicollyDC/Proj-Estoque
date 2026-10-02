import xml.etree.ElementTree as ET


def _processar_xml(raiz):
    """
    Processa uma NF-e a partir da raiz do XML.

    Retorna:
        nota, itens
    """

    # Remove namespaces das tags
    for elemento in raiz.iter():
        elemento.tag = elemento.tag.split("}")[-1]

    inf = raiz.find(".//infNFe")

    if inf is None:
        raise RuntimeError("Arquivo não é uma NF-e")

    def pegar(base, tag):
        if base is None:
            return ""

        return (base.findtext(tag) or "").strip()

    # ---------------- NOTA ---------------- #

    ide = inf.find("ide")
    emit = inf.find("emit")
    dest = inf.find("dest")

    chave = (
        inf.get("Id") or ""
    ).replace("NFe", "")

    nota = {
        "numero": pegar(ide, "nNF"),

        "fornecedor": pegar(
            emit,
            "xNome"
        ),

        "data": (
            pegar(ide, "dhEmi")
            or pegar(ide, "dEmi")
        )[:10],

        "chave": chave,

        "fornecedor_cnpj": pegar(
            emit,
            "CNPJ"
        ),

        "destinatario": pegar(
            dest,
            "xNome"
        ),

        "destinatario_cnpj": pegar(
            dest,
            "CNPJ"
        ),
    }

    # ---------------- ITENS ---------------- #

    itens = []

    for det in inf.findall("det"):

        prod = det.find("prod")

        if prod is None:
            continue

        itens.append({
            "codigo": pegar(
                prod,
                "cProd"
            ),

            "descricao": pegar(
                prod,
                "xProd"
            ),

            "qtd": float(
                pegar(prod, "qCom") or 0
            ),

            "unidade": pegar(
                prod,
                "uCom"
            ),

            "valor": float(
                pegar(prod, "vProd") or 0
            ),
        })

    return nota, itens


def ler_xml_nfe(caminho):
    """
    Lê uma NF-e a partir de um arquivo XML.
    """

    raiz = ET.parse(caminho).getroot()

    return _processar_xml(raiz)


def ler_xml_nfe_bytes(xml_bytes):
    """
    Lê uma NF-e recebida diretamente em memória.

    O XML não é salvo em arquivo.
    """

    if not xml_bytes:
        raise RuntimeError(
            "O XML recebido está vazio."
        )

    try:
        raiz = ET.fromstring(
            xml_bytes
        )

    except ET.ParseError as e:
        raise RuntimeError(
            f"Não foi possível interpretar o XML da NF-e: {e}"
        )

    return _processar_xml(raiz)