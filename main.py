
import os
import hashlib
import csv
from datetime import datetime

# Dossier a analyser
DOSSIER = os.path.expanduser(
    "~/storage/shared/Download"
)

# Emplacement du rapport
RAPPORT = os.path.expanduser(
    "~/ASS_PRO/reports/rapport.csv"
)

# Extensions a examiner
EXTENSIONS_SUSPECTES = [
    ".apk", ".exe", ".bat", ".sh",
    ".js", ".vbs", ".scr", ".ps1"
]


def calculer_sha256(chemin):
    empreinte = hashlib.sha256()

    with open(chemin, "rb") as fichier:
        for bloc in iter(
            lambda: fichier.read(1024 * 1024), b""
        ):
            empreinte.update(bloc)

    return empreinte.hexdigest()


def analyser_fichier(chemin):
    nom = os.path.basename(chemin)
    extension = os.path.splitext(nom)[1].lower()

    try:
        taille = os.path.getsize(chemin)
        empreinte = calculer_sha256(chemin)

        observations = []

        if taille == 0:
            observations.append("Fichier vide")

        if extension in EXTENSIONS_SUSPECTES:
            observations.append("Extension a examiner")

        if observations:
            statut = "A EXAMINER"
        else:
            statut = "AUCUN SIGNE DETECTE"

        return [
            nom, taille, empreinte,
            statut, "; ".join(observations)
        ]

    except OSError as erreur:
        return [
            nom, "", "", "ERREUR DE LECTURE", str(erreur)
        ]


def lancer_analyse():
    print("=" * 45)
    print("       ASS PRO - SECURITY SCANNER")
    print("=" * 45)

    if not os.path.isdir(DOSSIER):
        print("Dossier introuvable :", DOSSIER)
        return

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)

    total = 0

    with open(RAPPORT, "w", newline="", encoding="utf-8") as fichier_csv:

        rapport = csv.writer(fichier_csv)

        rapport.writerow([
            "Nom", "Taille", "SHA256",
            "Statut", "Observations"
        ])

        for racine, dossiers, fichiers in os.walk(DOSSIER):

            for nom in fichiers:
                chemin = os.path.join(racine, nom)

                resultat = analyser_fichier(chemin)
                rapport.writerow(resultat)

                total += 1

                if resultat[3] != "AUCUN SIGNE DETECTE":
                    print("[!]", nom, ":", resultat[3])

    print("\nANALYSE TERMINEE")
    print("Fichiers examines :", total)
    print("Rapport :", RAPPORT)


if __name__ == "__main__":
    lancer_analyse()
