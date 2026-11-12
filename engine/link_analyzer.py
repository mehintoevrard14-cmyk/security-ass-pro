
import re
import ipaddress
from urllib.parse import urlparse

RACCOURCISSEURS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "cutt.ly"
}

MARQUES = {
    "google": ["google.com"],
    "facebook": ["facebook.com"],
    "whatsapp": ["whatsapp.com"],
    "mtn": ["mtn.bj"],
    "amazon": ["amazon.com"]
}


def analyser_lien(lien):
    alertes = []

    if not isinstance(lien, str) or len(lien) > 2048:
        return {
            "statut": "INVALIDE",
            "domaine": None,
            "alertes": ["Entrée invalide"]
        }

    lien = lien.strip()

    if not lien:
        return {
         "statut": "A_VERIFIER",
         "domaine": None,
         "alertes": ["Lien vide ou absent"]
    }

    if not re.match(r"^https?://", lien, re.IGNORECASE):
        return {
            "statut": "A_VERIFIER",
            "domaine": None,
            "alertes": ["Protocole absent ou non HTTP(S)"]
        }

    try:
        url = urlparse(lien)

        # Vérification du protocole
        if url.scheme.lower() not in ("http", "https"):
            raise ValueError("Protocole non autorisé")

        domaine = url.hostname

        if not domaine:
            raise ValueError("Domaine absent")

        domaine = domaine.lower().rstrip(".")

        # Vérification du port
        port = url.port

        if port is not None and not (1 <= port <= 65535):
            raise ValueError("Port invalide")

        # Vérification de l'adresse IP
        try:
            ipaddress.ip_address(domaine)
            alertes.append("Adresse IP utilisée comme destination")
        except ValueError:
            pass

        # Vérification du nom de domaine
        if len(domaine) > 253:
            raise ValueError("Domaine trop long")

        if any(not partie for partie in domaine.split(".")):
            raise ValueError("Domaine mal formé")

        if any(
            not re.fullmatch(r"[a-z0-9-]+", partie)
            or partie.startswith("-")
            or partie.endswith("-")
            for partie in domaine.split(".")
        ):
            raise ValueError("Nom de domaine mal formé")

        # Détection des raccourcisseurs
        if domaine in RACCOURCISSEURS:
            alertes.append(
                "Lien raccourci : destination réelle inconnue"
            )

        # Détection HTTP
        if url.scheme.lower() == "http":
            alertes.append("Connexion HTTP non chiffrée")

        # Détection des identifiants dans l'adresse
        if url.username is not None or url.password is not None:
            alertes.append(
                "Identifiants présents dans l'adresse URL"
            )

        # Détection des noms IDN/Punycode
        if domaine.startswith("xn--") or ".xn--" in domaine:
            alertes.append(
                "Nom de domaine international à vérifier"
            )

        # Détection des imitations de marques
        for marque, domaines in MARQUES.items():
            if marque in domaine and not any(
                domaine == d or domaine.endswith("." + d)
                for d in domaines
            ):
                alertes.append(
                    "Domaine ressemblant à la marque " + marque
                )

        statut = "A_VERIFIER" if alertes else "AUCUN_INDICE"

        return {
            "statut": statut,
            "domaine": domaine,
            "alertes": alertes
        }

    except ValueError:
        return {
            "statut": "INVALIDE",
            "domaine": None,
            "alertes": ["Adresse ou port mal formé"]
        }

