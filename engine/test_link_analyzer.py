import unittest
from engine.link_analyzer import analyser_lien


class TestLinkAnalyzer(unittest.TestCase):

    def test_lien_https_normal(self):
        resultat = analyser_lien("https://example.com")
        self.assertEqual(resultat["statut"], "AUCUN_INDICE")

    def test_raccourcisseur(self):
        resultat = analyser_lien("https://bit.ly/abc123")
        self.assertEqual(resultat["statut"], "A_VERIFIER")

    def test_http(self):
        resultat = analyser_lien("http://example.com")
        self.assertEqual(resultat["statut"], "A_VERIFIER")

    def test_domaine_trompeur(self):
        resultat = analyser_lien("https://google.com.faux-site.test")
        self.assertEqual(resultat["statut"], "A_VERIFIER")

    def test_protocole_absent(self):
        resultat = analyser_lien("example.com")
        self.assertEqual(resultat["statut"], "A_VERIFIER")

    def test_entree_vide(self):
        resultat = analyser_lien("")
        self.assertEqual(resultat["statut"], "A_VERIFIER")


if __name__ == "__main__":
    unittest.main(verbosity=2)
