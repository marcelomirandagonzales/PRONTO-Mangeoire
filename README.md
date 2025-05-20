<div align="center">
  <h1>BirdNET-Analyzer</h1>
    <a href="https://birdnet-team.github.io/BirdNET-Analyzer/">
        <img src="https://github.com/birdnet-team/BirdNET-Analyzer/blob/main/docs/_static/logo_birdnet_big.png?raw=true" width="300" alt="BirdNET-Logo" />
    </a>
</div>
<br>
<div align="center">

Ce répertoire contient l'ensemble des codes nécessaires pour mettre en place le système que nous avons développé lors de notre projet PRONTO 2025. Il s'agit de mettre une place un système de mangeoire connectée en utilisant une Raspberry PI 3 et un PC serveur. 


Comment l'utiliser :

La Raspberry doit être équippé d'un capteur ultrason HC-SR04, d'une Pi Camera Module 2 et d'un microphone connecté par USB. Les étapes de fonctionnement sont les suivantes : lancer le code Raspberry_final_code sur la Raspberry dans un endroit suscpetible d'attirer l'attention d'oiseaux, lancer les deux autres codes présents sur le dossier programmes2025 sur un PC serveur connecté au même réseau WIFI que la Raspberry. Si un son est détecté par le microphone (à priori le chant d'un oiseau), celui ci réalisera un enregistrement audio qui sera transmis au PC et ensuite traité par une IA de reconnaissance. Un fichier contenant le nom des espèces d'oiseaux qui pourraient correspondre au chant enregistré sera ensuite disponible dans le dossier Results. Finalement, la Raspberry est aussi censée prendre des photos des oiseaux lorsque ceux-là s'approchent du capteur ultrasonore (distance inférieure à 15cm).


Pour plus d'informations concernant l'IA de reconnaissance, nous vous mettons à disposition le lien du Github où se trouve tout le modèle : 
https://github.com/birdnet-team/BirdNET-Analyzer/tree/main/birdnet_analyzer

