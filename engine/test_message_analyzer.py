import unittest
from engine.message_analyzer import analyser_message


class TestMessageAnalyzer(unittest.TestCase):

    def test_message_normal(self):
        message = (
            "Bonjour, la réunion est prévue demain "
            "à 10 heures. Merci de confirmer."
        )
        resultat = analyser_message(message)
        self.assertEqual(resultat["score"], 0)

    def test_faux_gain(self):
        message = (
            "Félicitations ! Vous avez gagné un prix. "
            "Envoyez de l'argent immédiatement."
        )
        resultat = analyser_message(message)
        self.assertGreaterEqual(resultat["score"], 60)
        self.assertEqual(resultat["niveau"], "ELEVE")

    def test_message_vide(self):
        resultat = analyser_message("")
        self.assertEqual(resultat["statut"], "ERREUR")

    def test_lien(self):
        message = "Visitez https://example.com"
        resultat = analyser_message(message)
        self.assertEqual(len(resultat["liens"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
