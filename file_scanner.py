
import os
import hashlib
import json
import subprocess
from datetime import datetime

# ==========================================
# CONFIGURATION ASS PRO
# ==========================================

DOSSIER_REGLES = "rules"

EXTENSIONS_SUSPECTES = {
    ".apk", ".exe", ".bat", ".cmd",
    ".scr", ".vbs", ".js", ".ps1"
}


# ==========================================
# CALCUL SHA256
# ==========================================

def calculer_sha256(chemin):
    """Calcule l'empreinte SHA256 d'un fichier."""

    sha256 = hashlib.sha256()

    try:
        with open(chemin, "rb") as fichier:
            for bloc in iter(lambda: fichier.read(65536), b""):
                sha256.update(bloc)

        return sha256.hexdigest()

    except OSError:
        return None


# ==========================================
# DETECTInano file_scanner.py====================================

def detecter_yara(chemin):
    alertes = []

    if not os.path.isdir(DOSSIER_REGLES):
        return alertes

    for nom in os.listdir(DOSSIER_REGLES):
        if not nom.endswith(".yar"):
            continue

        regle = os.path.join(DOSSIER_REGLES, nom)

        try:
            resultat = subprocess.run(
                ["yara", regle, chemin],
                capture_output=True,
                text=True,
                timeout=20
            )

            if resultat.returncode == 0:
                lignes = resultat.stdout.strip().splitlines()

                for ligne in lignes:
                    if ligne.strip():
                        alertes.append(ligne.strip())

            elif resultat.returncode > 1:
                message = resultat.stderr.strip()
                alertes.append(
                    "ERREUR YARA : " + (message or "Erreur inconnue")
                )

        except subprocess.TimeoutExpired:
            alertes.append("ERREUR : délai YARA dépassé")

        except OSError as erreur:
            alertes.append("ERREUR : " + str(erreur))

    return alertes


# ==========================================
# ANALYSE D'UN FICHIER
# ==========================================

def analyser_fichier(chemin):
    """Analyse les caractéristiques d'un fichier."""

    resultat = {
        "fichier": chemin,
        "date_analyse": datetime.now().isoformat(),
        "sha256": None,
        "taille": None,
        "statut": "SAIN",
        "alertes": []
    }

    try:

        if not os.path.isfile(chemin):
            resultat["statut"] = "ERREUR"
            resultat["alertes"].append(
                "Fichier inaccessible"
            )
            return resultat

        # Taille du fichier
        resultat["taille"] = os.path.getsize(chemin)

        # Calcul SHA256
        resultat["sha256"] = calculer_sha256(chemin)

        if resultat["sha256"] is None:
            resultat["statut"] = "ERREUR"
            resultat["alertes"].append(
                "Lecture impossible"
            )
            return resultat

        # Vérification de l'extension
        extension = os.path.splitext(chemin)[1].lower()

        if extension in EXTENSIONS_SUSPECTES:
            resultat["statut"] = "A_VERIFIER"

            resultat["alertes"].append(
                "Extension pouvant contenir du code exécutable"
            )

        # Détection avec YARA
        alertes_yara = detecter_yara(chemin)

        if alertes_yara:
            resultat["statut"] = "DETECTION"

            resultat["alertes"].extend(
                alertes_yara
            )

        # Vérification des fichiers vides
        if resultat["taille"] == 0:
            resultat["alertes"].append(
                "Fichier vide"
            )

    except OSError as erreur:

        resultat["statut"] = "ERREUR"

        resultat["alertes"].append(
            str(erreur)
        )

    return resultat


# ==========================================
# ANALYSE D'UN DOSSIER
# ==========================================

def analyser_dossier(dossier):
    """Analyse tous les fichiers d'un dossier."""

    resultats = []

    for racine, dossiers, fichiers in os.walk(dossier):

        for nom in fichiers:

            chemin = os.path.join(racine, nom)

            resultat = analyser_fichier(chemin)

            resultats.append(resultat)

            print(
                f"[{resultat['statut']}] {chemin}"
            )

            # Affichage des alertes
            for alerte in resultat["alertes"]:

                print("  ->", alerte)

    # Création du dossier des rapports
    os.makedirs("reports", exist_ok=True)

    # Construction du rapport
    rapport = {
        "date": datetime.now().isoformat(),
        "nombre_fichiers": len(resultats),
        "resultats": resultats
    }

    # Enregistrement JSON
    with open(
        "reports/scan_report.json",
        "w",
        encoding="utf-8"
    ) as fichier:

        json.dump(
            rapport,
            fichier,
            indent=4,
            ensure_ascii=False
        )

    print("\n================================")
    print("ANALYSE ASS PRO TERMINEE")
    print("================================")

    print("Nombre de fichiers :", len(resultats))

    print(
        "Rapport : reports/scan_report.json"
    )


# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================

if __name__ == "__main__":

    print("==============================")
    print(" ASS PRO - SECURITY SCANNER")
    print("==============================")

    dossier = input(
        "Dossier à analyser : "
    ).strip()

    if os.path.isdir(dossier):

        analyser_dossier(dossier)

    else:

        print("Erreur : dossier introuvable.")

