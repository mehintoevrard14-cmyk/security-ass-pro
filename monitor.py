
import os
import json
import hashlib
from datetime import datetime

DOSSIER = "zone_test"
BASELINE = "baseline.json"
JOURNAL = "journal.log"


def calculer_hash(chemin):
    sha = hashlib.sha256()

    with open(chemin, "rb") as fichier:
        for bloc in iter(lambda: fichier.read(4096), b""):
            sha.update(bloc)

    return sha.hexdigest()


def scanner_dossier():
    resultats = {}

    for racine, dossiers, fichiers in os.walk(DOSSIER):
        for nom in fichiers:
            chemin = os.path.join(racine, nom)

            try:
                resultats[chemin] = calculer_hash(chemin)
            except (OSError, PermissionError) as erreur:
                print("[ERREUR]", chemin, erreur)

    return resultats


def enregistrer_evenement(message):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(JOURNAL, "a") as fichier:
        fichier.write(f"[{date}] {message}\n")

    print(message)


def initialiser():
    os.makedirs(DOSSIER, exist_ok=True)

    reference = scanner_dossier()

    with open(BASELINE, "w") as fichier:
        json.dump(reference, fichier, indent=4)

    print("[OK] Reference initiale enregistree.")
    print("Fichiers surveilles :", len(reference))


def verifier():
    if not os.path.exists(BASELINE):
        print("[ERREUR] Lancez init d'abord.")
        return

    with open(BASELINE, "r") as fichier:
        ancienne = json.load(fichier)

    actuelle = scanner_dossier()

    anciens = set(ancienne)
    nouveaux = set(actuelle)

    modifies = anciens & nouveaux
    supprimes = anciens - nouveaux
    ajoutes = nouveaux - anciens

    total = 0

    for chemin in modifies:
        if ancienne[chemin] != actuelle[chemin]:
            enregistrer_evenement(
                f"[MODIFIE] {chemin}"
            )
            total += 1

    for chemin in supprimes:
        enregistrer_evenement(
            f"[SUPPRIME] {chemin}"
        )
        total += 1

    for chemin in ajoutes:
        enregistrer_evenement(
            f"[NOUVEAU] {chemin}"
        )
        total += 1

    if total == 0:
        print("[OK] Aucun changement detecte.")
    else:
        print("\nNombre d'evenements :", total)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        initialiser()

    elif len(sys.argv) > 1 and sys.argv[1] == "check":
        verifier()

    else:
        print("ASS PRO - FILE MONITOR")
        print("python monitor.py init")
        print("python monitor.py check")

