import hashlib

def calculer_sha256(nom_fichier):

    sha256 = hashlib.sha256()

    with open(nom_fichier, "rb") as fichier:

        while True:
            bloc = fichier.read(4096)

            if not bloc:
                break

            sha256.update(bloc)

    return sha256.hexdigest()


empreinte = calculer_sha256("test.txt")

print("Fichier : test.txt")
print("SHA256 :", empreinte)
