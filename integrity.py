
import os
import sys
import json
import hashlib

DOSSIER = os.path.expanduser("~/storage/shared/Download")
BASELINE = "reports/integrity_baseline.json"


def calculer_hash(chemin):
    sha = hashlib.sha256()

    with open(chemin, "rb") as fichier:
        for bloc in iter(lambda: fichier.read(4096), b""):
            sha.update(bloc)

    return sha.hexdigest()


def analyser_dossier():
    empreintes = {}

    for racine, dossiers, fichiers in os.walk(DOSSIER):
        for nom in fichiers:
            chemin = os.path.join(racine, nom)

            try:
                relatif = os.path.relpath(chemin, DOSSIER)
                empreintes[relatif] = calculer_hash(chemin)

            except (OSError, PermissionError) as erreur:
                print("[ERREUR]", chemin, erreur)

    return empreintes


def initialiser():
    empreintes = analyser_dossier()

    with open(BASELINE, "w") as fichier:
        json.dump(empreintes, fichier, indent=4)

    print("[OK] Référence enregistrée")
    print("Fichiers enregistrés :", len(empreintes))


def verifier():
    if not os.path.exists(BASELINE):
        print("[!] Lance init d'abord.")
        return

    with open(BASELINE, "r") as fichier:
        anciennes = json.load(fichier)

    actuelles = analyser_dossier()

    anciens_noms = set(anciennes)
    nouveaux_noms = set(actuelles)

    ajoutes = nouveaux_noms - anciens_noms
    supprimes = anciens_noms - nouveaux_noms
    communs = anciens_noms & nouveaux_noms

    modifies = [
        nom for nom in communs
        if anciennes[nom] != actuelles[nom]
    ]

    print("\n===== RAPPORT D'INTEGRITE =====")

    print("\n[+] Nouveaux fichiers :", len(ajoutes))
    for nom in sorted(ajoutes):
        print("[NOUVEAU]", nom)

    print("\n[-] Fichiers supprimés :", len(supprimes))
    for nom in sorted(supprimes):
        print("[SUPPRIME]", nom)

    print("\n[!] Fichiers modifiés :", len(modifies))
    for nom in sorted(modifies):
        print("[MODIFIE]", nom)

    if not ajoutes and not supprimes and not modifies:
        print("\n[OK] Aucun changement détecté.")

    print("\n===== ANALYSE TERMINEE =====")


if __name__ == "__main__":

    os.makedirs("reports", exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        initialiser()

    elif len(sys.argv) > 1 and sys.argv[1] == "check":
        verifier()

    else:
        print("Utilisation :")
        print("python integrity.py init")
        print("python integrity.py check")

