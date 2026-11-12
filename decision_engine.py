
import os
import json
import shutil
from datetime import datetime

RAPPORT = "reports/scan_report.json"
QUARANTAINE = "quarantine"
JOURNAL = "reports/decisions.json"

# Aucune règle fiable n'est encore configurée.
# Notre règle pédagogique ne doit jamais être considérée
# comme une preuve de virus.
REGLES_FIABLES = set()


def enregistrer_decision(decision):
    os.makedirs("reports", exist_ok=True)

    historique = []

    if os.path.exists(JOURNAL):
        try:
            with open(JOURNAL, "r", encoding="utf-8") as f:
                historique = json.load(f)
            if not isinstance(historique, list):
                historique = []
        except (OSError, json.JSONDecodeError):
            historique = []

    historique.append(decision)

    with open(JOURNAL, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4, ensure_ascii=False)


def isoler_fichier(chemin):
    os.makedirs(QUARANTAINE, exist_ok=True)

    destination = os.path.join(
        QUARANTAINE,
        os.path.basename(chemin)
    )

    if os.path.exists(destination):
        return False, "Nom déjà présent dans la quarantaine"

    try:
        shutil.move(chemin, destination)
        return True, destination
    except OSError as erreur:
        return False, str(erreur)


def analyser_decisions():
    if not os.path.isfile(RAPPORT):
        print("Rapport introuvable. Lance d'abord le scanner.")
        return

    try:
        with open(RAPPORT, "r", encoding="utf-8") as f:
            rapport = json.load(f)
    except (OSError, json.JSONDecodeError):
        print("Impossible de lire le rapport.")
        return

    print("\n==============================")
    print(" ASS PRO - MOTEUR DE DECISION")
    print("==============================")

    for resultat in rapport.get("resultats", []):
        chemin = resultat.get("fichier", "")
        alertes = resultat.get("alertes", [])
        statut = resultat.get("statut", "")

        alertes = [
            a for a in alertes
            if isinstance(a, str) and a.strip()
        ]

        regles_detectees = [
            a.split()[0] for a in alertes
            if not a.startswith("ERREUR")
        ]

        decision = "AUCUNE ACTION"
        motif = ""
        destination = None

        if statut == "ERREUR" or any(
            a.startswith("ERREUR") for a in alertes
        ):
            decision = "ANALYSE INCOMPLETE"
            motif = "Impossible de garantir une analyse correcte."

        elif not os.path.isfile(chemin):
            decision = "FICHIER INTROUVABLE"
            motif = "Le fichier n'existe plus à son emplacement."

        elif any(r in REGLES_FIABLES for r in regles_detectees):
            succes, resultat_action = isoler_fichier(chemin)

            if succes:
                decision = "QUARANTAINE AUTOMATIQUE"
                motif = "Signature fiable reconnue."
                destination = resultat_action
            else:
                decision = "ALERTE - NON ISOLE"
                motif = resultat_action

        elif regles_detectees:
            decision = "ALERTE - OBSERVATION"
            motif = (
                "Signature détectée, mais non encore validée "
                "comme fiable."
            )

        elif statut == "DETECTION":
            decision = "ALERTE - A VERIFIER"
            motif = "Détection sans signature exploitable."

        elif statut == "A_VERIFIER":
            decision = "OBSERVATION"
            motif = "Caractéristique suspecte, non suffisante pour conclure."

        else:
            decision = "FICHIER NON SIGNALE"
            motif = "Aucun indice suspect détecté."

        element = {
            "date": datetime.now().isoformat(),
            "fichier": chemin,
            "decision": decision,
            "motif": motif,
            "destination": destination
        }

        enregistrer_decision(element)

        print(f"\nFichier : {chemin}")
        print(f"Décision : {decision}")
        print(f"Motif : {motif}")

    print("\nDécisions enregistrées dans :", JOURNAL)


if __name__ == "__main__":
    analyser_decisions()

