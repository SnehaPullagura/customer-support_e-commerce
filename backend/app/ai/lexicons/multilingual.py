"""
Multilingual Customer Support Synonym Banks & Intent Translators (EN, ES, FR, DE, IT, PT, JA, ZH).
"""

from typing import Dict, List


MULTILINGUAL_INTENT_SYNONYMS: Dict[str, Dict[str, List[str]]] = {
    # Spanish (ES)
    "es": {
        "DAMAGED_PRODUCT": [
            "dañado", "roto", "averiado", "paquete aplastado", "caja rota", "pantalla rota",
            "llegó roto", "producto dañado", "artículo roto", "defecto de fábrica",
        ],
        "LATE_DELIVERY": [
            "donde esta mi pedido", "mi paquete no llega", "retraso en entrega", "pedido tarde",
            "rastreo sin movimiento", "cuando llega mi paquete", "retrasado",
        ],
        "MARKED_DELIVERED_NOT_RECEIVED": [
            "dice entregado pero no lo tengo", "no recibí mi paquete", "paquete robado", "no me llegó",
        ],
        "DOUBLE_CHARGED": [
            "cobro doble", "me cobraron dos veces", "cargo duplicado", "cobro no autorizado",
        ],
        "REQUEST_RETURN_LABEL": [
            "etiqueta de devolución", "quiero devolver", "hacer una devolución", "cambiar talla",
        ],
        "CANCEL_ORDER": [
            "cancelar pedido", "anular compra", "error en pedido", "cancelar antes de enviar",
        ],
    },

    # French (FR)
    "fr": {
        "DAMAGED_PRODUCT": [
            "endommagé", "cassé", "abîmé", "colis écrasé", "boîte déchirée", "écran fissuré",
            "arrivé cassé", "produit défectueux", "article abîmé",
        ],
        "LATE_DELIVERY": [
            "où est mon colis", "colis en retard", "retard de livraison", "suivi bloqué",
            "quand arrive ma commande", "commande non reçue",
        ],
        "MARKED_DELIVERED_NOT_RECEIVED": [
            "marqué livré mais rien reçu", "colis non reçu", "colis volé", "pas reçu",
        ],
        "DOUBLE_CHARGED": [
            "double facturation", "débité deux fois", "facturation en double", "prélèvement erroné",
        ],
        "REQUEST_RETURN_LABEL": [
            "étiquette de retour", "je veux retourner", "renvoyer article", "échange de taille",
        ],
        "CANCEL_ORDER": [
            "annuler commande", "annuler mon achat", "erreur de commande",
        ],
    },

    # German (DE)
    "de": {
        "DAMAGED_PRODUCT": [
            "beschädigt", "kaputt", "zerbrochen", "paket zerdrückt", "karton beschädigt", "display gesprungen",
            "kaputt angekommen", "defektes produkt", "ware defekt",
        ],
        "LATE_DELIVERY": [
            "wo ist mein paket", "paket verspätet", "lieferverzögerung", "sendungsverfolgung hängt",
            "wann kommt die bestellung", "noch nicht geliefert",
        ],
        "MARKED_DELIVERED_NOT_RECEIVED": [
            "als zugestellt markiert aber nicht erhalten", "paket nicht angekommen", "paket gestohlen",
        ],
        "DOUBLE_CHARGED": [
            "doppelt abgebucht", "zweimal bezahlt", "doppelte buchung", "falscher betrag",
        ],
        "REQUEST_RETURN_LABEL": [
            "rücksendeschein", "möchte zurücksenden", "retoure erstellen", "umtauschen",
        ],
        "CANCEL_ORDER": [
            "bestellung stornieren", "kauf abbrechen", "versehentlich bestellt",
        ],
    },

    # Italian (IT)
    "it": {
        "DAMAGED_PRODUCT": [
            "danneggiato", "rotto", "pacco schiacciato", "scatola rotta", "schermo rotto", "arrivato rotto",
        ],
        "LATE_DELIVERY": [
            "dov'è il mio pacco", "ordine in ritardo", "ritardo consegna", "tracking bloccato",
        ],
        "DOUBLE_CHARGED": [
            "doppio addebito", "addebitato due volte", "pagamento duplicato",
        ],
        "REQUEST_RETURN_LABEL": [
            "etichetta di reso", "voglio restituire", "fare un reso",
        ],
        "CANCEL_ORDER": [
            "annullare ordine", "cancellare ordine",
        ],
    },

    # Portuguese (PT)
    "pt": {
        "DAMAGED_PRODUCT": [
            "danificado", "quebrado", "embalagem amassada", "caixa rasgada", "tela trincada", "chegou quebrado",
        ],
        "LATE_DELIVERY": [
            "onde está meu pedido", "encomenda atrasada", "atraso na entrega", "rastreio parado",
        ],
        "DOUBLE_CHARGED": [
            "cobrança dupla", "cobrado duas vezes", "pagamento duplicado",
        ],
        "REQUEST_RETURN_LABEL": [
            "etiqueta de devolução", "quero devolver", "fazer devolução",
        ],
        "CANCEL_ORDER": [
            "cancelar pedido", "cancelar compra",
        ],
    },

    # Japanese (JA)
    "ja": {
        "DAMAGED_PRODUCT": [
            "破損", "壊れている", "箱が潰れている", "画面が割れている", "初期不良", "届いた時に壊れていた",
        ],
        "LATE_DELIVERY": [
            "荷物はどこですか", "配送遅延", "届かない", "追跡が動かない", "いつ届きますか",
        ],
        "DOUBLE_CHARGED": [
            "二重請求", "2回引き落とされた", "重複決済",
        ],
        "REQUEST_RETURN_LABEL": [
            "返品したい", "返品用ラベル", "返送手続き", "サイズ交換",
        ],
        "CANCEL_ORDER": [
            "注文をキャンセルしたい", "キャンセル希望", "誤注文",
        ],
    },

    # Mandarin Chinese (ZH)
    "zh": {
        "DAMAGED_PRODUCT": [
            "破损", "坏了", "包装破损", "屏幕碎了", "损坏", "收到时坏了", "有质量问题",
        ],
        "LATE_DELIVERY": [
            "包裹在哪里", "物流延迟", "没有收到", "物流没有更新", "快递延迟",
        ],
        "DOUBLE_CHARGED": [
            "重复扣款", "扣了两次钱", "重复收费",
        ],
        "REQUEST_RETURN_LABEL": [
            "申请退货", "退货退款", "换货", "退货标签",
        ],
        "CANCEL_ORDER": [
            "取消订单", "不想要了", "买错了",
        ],
    },
}


class MultilingualIntentMatcher:
    @staticmethod
    def match_multilingual_intent(text: str) -> Optional[str]:
        lower = text.lower().strip()
        for lang, intent_dict in MULTILINGUAL_INTENT_SYNONYMS.items():
            for intent, synonyms in intent_dict.items():
                for syn in synonyms:
                    if syn in lower:
                        return intent
        return None
