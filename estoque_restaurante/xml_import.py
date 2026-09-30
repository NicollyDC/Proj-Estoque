import xml.etree.ElementTree as ET

from estoque_restaurante.app_state import marcar_alteracao
from estoque_restaurante.ui.notas import nota_refresh


def ler_xml_nfe(caminho):
    raiz = ET.parse(caminho).getroot()

    for elemento in raiz.iter():
        elemento.tag = elemento.tag.split("}")[-1]

    inf = raiz.find(".//infNFe")

    if inf is None:
        raise RuntimeError("Arquivo não é uma NF-e")

    def pegar(base, tag):
        if base is None:
            return ""

        return (base.findtext(tag) or "").strip()

    ide = inf.find("ide")
    emit = inf.find("emit")

    nota = {
        "numero": pegar(ide, "nNF"),
        "fornecedor": pegar(emit, "xNome"),
        "data": (pegar(ide, "dhEmi") or pegar(ide, "dEmi"))[:10],
        "chave": (inf.get("Id") or "").replace("NFe", "")
    }

    itens = []

    for det in inf.findall("det"):
        prod = det.find("prod")

        itens.append({
            "codigo": pegar(prod, "cProd"),
            "descricao": pegar(prod, "xProd"),
            "qtd": float(pegar(prod, "qCom") or 0),
            "unidade": pegar(prod, "uCom"),
            "valor": float(pegar(prod, "vProd") or 0)
        })

    marcar_alteracao()
    nota_refresh()

    return nota, itens