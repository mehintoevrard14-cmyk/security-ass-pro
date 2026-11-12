
import os
import json
import shutil
import hashlib
from datetime import datetime

DOSSIER_QUARANTAINE = "quarantine"
REGISTRE = "reports/quarantine_registry.json"


def calculer_hash(chemin):
    sha256 = hashlib.sha256()

    with open(chemin, "rb") as fichier:
        for bloc in iter(lambda: fichier.read(65536), b""):
            sha256.update(bloc)

    return sha256.hexdigest()


def charger_registre():
    os.makedirs("reports", exist_ok=True)

    if not os.path.exists(REGISTRE):
        return []

    try:
        with open(REGISTRE, "r", encoding="utf-8") as fichier:
            return json.load(fichier)
    except (OSError, json.JSONDecodeError):
        print("Erreur : registre illisible.")
        return None


def mettre_en_quarantaine(chemin):
    if not os.path.isfile(chemin):
        print("Fichier introuvable.")
        return

    registre = charger_registre()

    if registre is None:
        return

    chemin_absolu = os.path.abspath(chemin)
    empreinte = calculer_hash(chemin_absolu)

    nom = os.path.basename(chemin)
    date = datetime.now().strftime("%Y%m%d_%H%M%S")

    destination = os.path.join(
        DOSSIER_QUARANTAINE,
        f"{date}_{empreinte[:12]}_{nom}"
    )

    print("\nFichier :", chemin_absolu)
    print("SHA256 :", empreinte)
    print("Destination :", destination)

    confirmation = input(
        "\nConfirmer la mise en quarantaine ? (oui/non) : "
    ).strip().lower()

    if confirmation != "oui":
        print("Opération annulée.")
        return

    os.makedirs(DOSSIER_QUARANTAINE, exist_ok=True)

    try:
        shutil.move(chemin_absolu, destination)

        registre.append({
            "original": chemin_absolu,
            "quarantaine": destination,
            "sha256": empreinte,
            "date": datetime.now().isoformat()
        })

        with open(REGISTRE, "w", encoding="utf-8") as fichier:
            json.dump(
                registre,
                fichier,
                indent=4,
                ensure_ascii=False
            )

        print("Fichier placé en quarantaine.")

    except OSError as erreur:
        print("Erreur :", erreur)


def lister_quarantaine():
    registre = charger_registre()

    if registre is None:
        return

    if not registre:
        print("La quarantaine est vide.")
        return

    for numero, element in enumerate(registre, start=1):
        print(f"\n{numero}. {element['original']}")
        print("   Stockage :", element["quarantaine"])
        print("   SHA256 :", element["sha256"])


if __name__ == "__main__":
    print("ASS PRO - QUARANTAINE")
    print("1. Isoler un fichier")
    print("2. Afficher les fichiers isolés")

    choix = input("Ton choix : ").strip()

    if choix == "1":
        chemin = input("Chemin du fichier : ").strip()
        mettre_en_quarantaine(chemin)

    elif choix == "2":
        lister_quarantaine()

    else:
        print("Choix invalide.")

