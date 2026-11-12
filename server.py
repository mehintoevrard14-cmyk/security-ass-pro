import os
import uuid
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from file_scanner import analyser_fichier

BASE_DIR = Path(__file__).resolve().parent
INTERFACE_DIR = BASE_DIR / "interface"
UPLOAD_DIR = BASE_DIR / "runtime_uploads"

UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


@app.get("/")
def accueil():
    return send_from_directory(INTERFACE_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({
        "application": "ASS PRO",
        "api": "operationnelle"
    })


@app.errorhandler(413)
def fichier_trop_volumineux(error):
    return jsonify({
        "erreur": "Fichier trop volumineux. Limite : 20 Mo."
    }), 413


@app.post("/api/scan")
def scan():
    if "file" not in request.files:
        return jsonify({"erreur": "Aucun fichier reçu."}), 400

    fichier = request.files["file"]

    if not fichier.filename:
        return jsonify({"erreur": "Nom de fichier manquant."}), 400

    nom = secure_filename(fichier.filename)

    if not nom:
        return jsonify({"erreur": "Nom de fichier invalide."}), 400

    chemin = UPLOAD_DIR / f"{uuid.uuid4().hex}_{nom}"

    try:
        fichier.save(chemin)

        resultat = analyser_fichier(str(chemin))

        # Ne pas révéler le chemin interne du serveur.
        resultat.pop("fichier", None)
        resultat["nom_fichier"] = nom

        return jsonify(resultat)

    except Exception:
        app.logger.exception("Erreur pendant l'analyse")
        return jsonify({
            "erreur": "Une erreur interne est survenue."
        }), 500

    finally:
        if chemin.exists():
            chemin.unlink()


if __name__ == "__main__":
    print("ASS PRO API : http://127.0.0.1:8080")
    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False
    )
