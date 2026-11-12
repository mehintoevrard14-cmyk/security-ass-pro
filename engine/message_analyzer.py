
import re
from engine.link_analyzer import analyser_lien

# ASS PRO - Communication Guard

REGLES = {
    "demande_argent": {
        "mots": ["envoyez de l'argent", "transfert d'argent",
                 "frais de retrait", "payez maintenant"],
        "points": 25
    },
    "faux_gain": {
        "mots": ["vous avez gagné", "vous êtes gagnant",
                 "prix à réclamer", "réclamez votre cadeau"],
        "points": 25
    },
    "urgence": {
        "mots": ["immédiatement", "dans les 5 minutes",
                 "dernier avertissement", "compte bloqué"],
        "points": 15
    },
    "vol_identifiants": {
        "mots": ["mot de passe", "code otp",
                 "code de vérification", "identifiants"],
        "points": 20
    },
    "menace": {
        "mots": ["votre compte sera supprimé",
                 "votre compte sera suspendu",
                 "action judiciaire"],
        "points": 15
    }
}


def extraire_liens(texte):
    expression = r'https?://[^\s<>"\']+'
    return re.findall(expression, texte, re.IGNORECASE)


def analyser_message(texte):
    if not isinstance(texte, str) or not texte.strip():
        return {
            "statut": "ERREUR",
            "score": 0,
            "niveau": "INDETERMINE",
            "alertes": [],
            "liens": [],
            "analyses_liens": []
        }

    texte_min = texte.lower()
    alertes = []
    score = 0

    # Analyse du contenu du message
    for nom, regle in REGLES.items():
        for mot in regle["mots"]:
            if mot in texte_min:
                alertes.append(nom + " : " + mot)
                score += regle["points"]
                break

    # Extraction et analyse des liens
    liens = extraire_liens(texte)
    analyses_liens = []

    for lien in liens:
        resultat_lien = analyser_lien(lien)
        analyses_liens.append(resultat_lien)

        if resultat_lien["statut"] == "A_VERIFIER":
            alertes.append("LIEN A VERIFIER : " + lien)
            score += 30

        elif resultat_lien["statut"] == "INVALIDE":
            alertes.append("LIEN INVALIDE : " + lien)
            score += 15

    score = min(score, 100)

    if score >= 60:
        niveau = "ELEVE"
    elif score >= 30:
        niveau = "MOYEN"
    else:
        niveau = "FAIBLE"

    return {
        "statut": "ANALYSE_TERMINEE",
        "score": score,
        "niveau": niveau,
        "alertes": alertes,
        "liens": liens,
        "analyses_liens": analyses_liens
    }


if __name__ == "__main__":
    print("\n=== ASS PRO COMMUNICATION GUARD ===")
    print("Colle ton message.")
    print("Tape FIN sur une ligne seule pour terminer.\n")

    lignes = []

    while True:
        ligne = input()
        if ligne.strip().upper() == "FIN":
            break
        lignes.append(ligne)

    message = "\n".join(lignes)
    resultat = analyser_message(message)

    print("\n=== RESULTAT ===")
    print("Score :", resultat["score"], "/100")
    print("Risque :", resultat["niveau"])

    print("\nAlertes :")
    for alerte in resultat["alertes"]:
        print("-", alerte)

    print("\nRésultats détaillés des liens :")
    for analyse in resultat["analyses_liens"]:
        print("- Statut :", analyse["statut"])
        print("  Domaine :", analyse.get("domaine", "Inconnu"))
        for alerte in analyse["alertes"]:
            print("  Alerte :", alerte)

    if not resultat["alertes"]:
        print("Aucun indice connu détecté.")

    print("\nAnalyse indicative : vérification humaine recommandée.")

