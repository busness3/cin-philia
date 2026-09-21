# a_monter/ — boîte de réception des rushs

Dossier de passage pour envoyer un rush à monter depuis un appareil sans
accès terminal (iPad). Fonctionnement :

1. Cléa dépose un fichier vidéo ici via l'upload web de GitHub (voir le
   guide privé pour le pas-à-pas).
2. Elle le signale dans la conversation avec Claude.
3. Claude récupère le fichier (`git pull`), monte la vidéo, puis **supprime
   le rush de ce dossier** une fois le montage terminé — pour ne pas
   alourdir le dépôt avec des vidéos brutes qui n'ont plus besoin d'y être.

Le rendu final n'est jamais poussé ici : il est renvoyé directement dans la
conversation (pièce jointe), pas stocké dans le repo.

**Limite pratique** : l'upload web GitHub plafonne autour de 25 Mo par
fichier. Un rush plus lourd doit être compressé/raccourci avant l'envoi
(qualité source moindre, sans grand impact puisque tout est de toute façon
réencodé au format final).
