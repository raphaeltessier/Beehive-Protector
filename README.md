# Beehive-Protector
Projet d'initiation à la recherche, protection d'une ruche contre les frelons asiatiques par IA et tapette automatique.
Voir rapport pour plus de détail.

## Analyse Fréquentielle
Script disponible dans Freq_Anal, base de données audio "To bee or no to bee" de Kaggle 
-> résultats très peu concluant

## Analyse d'image
Utilisation jetson nano, voir doc developer kit pour installation
First boot bash script disponible (firstboot.sh) pour modifier la ram allouer (nécéssité de redémarré la carte après).
script bash setup.sh installe la quasi totalité des librairies nécéssaires à l'utilisation de ia.py.
Audio.py : acquisition audio de 3s depuis la caméra.
ia.py : script d'analyse image en temps réel. Doit être optimiser pour prendre plus d'image à la seconde (configurer conda (pilote graphique) pour faire tourner le programme dessus). Nécéssité d'activer des paramètres cachés lors du boot pour autorisé l'activation de la pwm (https://www.youtube.com/watch?v=eImDQ0PVu2Y) permettant de commander le moteur après détection. base de données d'image annoté sur https://universe.roboflow.com/pir/hornetv2

## Tapette automatique 
modèle 3d des composants disponible dans 3D-models/print_data_2
