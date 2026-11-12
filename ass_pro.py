
import subprocess
import sys
import os

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))

def lancer_programme(nom):
    chemin = os.path.join(DOSSIER_PROJET, nom)

    if not os.path.isfile(chemin):
        print("Erreur : fichier introuvable :", nom)
        return False

    resultat = subprocess.run(
        [sys.executable, chemin],
        cwd=DOSSIER_PROJET
    )

    return resultat.returncode == 0


def menu():
    while True:
        print("\n================================")
        print("       ASS PRO SECURITY")
        print("================================")
        print("1. Lancer une analyse complète")
        print("2. Consulter les décisions")
        print("3. Quitter")

        choix = input("\nTon choix : ").strip()

        if choix == "1":
            if lancer_programme("file_scanner.py"):
                lancer_programme("decision_engine.py")

        elif choix == "2":
            fichier = os.path.join(
                DOSSIER_PROJET,
                "reports",
                "decisions.json"
            )

            if os.path.isfile(fichier):
                with open(fichier, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print("Aucune décision enregistrée.")

        elif choix == "3":
            print("ASS PRO arrêté.")
            break

        else:
            print("Choix invalide.")


if __name__ == "__main__":
    menu()

