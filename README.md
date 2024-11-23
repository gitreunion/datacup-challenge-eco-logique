# La Réunion DataCup Challenge 2024 - Eco-Logique
La [Réunion DataCup Challenge](https://data.regionreunion.com/p/page-reunion-datacup-challenge) est un événement unique où toutes les compétences en manipulation de données sont mises à l’honneur : extraction, traitement, modélisation… Porté par la Région Réunion, *La Réunion DataCup Challenge* s'inscrit dans un cadre de coopération avec les producteurs de données du territoire souhaitant ouvrir, mutualiser et valoriser leurs données. Les thématiques des partenaires sont variées : de la préservation des ressources à l’économie, ou encore des préoccupations des collectivités territoriales et de leurs habitants.

L’objectif de cette seconde édition est de continuer à fédérer une communauté autour des données ouvertes du territoire ainsi qu'initier des projets pérennisables et utiles au plus grand nombre.


## Eco-Logique
Notre équipe a choisi de répondre au défi "Catch water if you can" porté par l’Office de l’eau.
Ce défi s'inscrit dans une démarche visant à préserver cette ressource essentielle qui est l’eau. Face aux besoins croissants et à la raréfaction de cette ressource, en particulier durant la saison sèche, il devient indispensable de repenser nos usages et de proposer des solutions durables pour réduire notre consommation. En encourageant la récupération des eaux pluviales, notamment pour des usages tels que l’arrosage extérieur ou l’alimentation des WC, l’Office de l’eau Réunion ambitionne de promouvoir des pratiques responsables et adaptées aux spécificités locales.

Il a pour objectif de proposer un outil ergonomique et innovant qui permettra d’évaluer le volume d’eau de pluie récupérable en fonction de la localisation géographique et de la surface de toiture, tout en prenant en compte les besoins spécifiques liés aux usages des bénéficiaires. Cet outil offrira également la possibilité de calculer le volume optimal d’une cuve de récupération ainsi que les économies potentielles, que ce soit en termes de préservation de la ressource en eau ou de réduction de la facture d’eau. En intégrant une visualisation ludique et interactive des résultats, avec des graphiques, des données ajustables et des éléments cliquables, il vise à rendre l’expérience utilisateur engageante et pédagogique. Conçu pour être autonome et facilement actualisable, il sera intégré sur le site de l’Office de l’eau Réunion afin de sensibiliser durablement à l’importance de la sobriété des usages et au potentiel de récupération d’eau de pluie.


## Documentation
Notre solution répond au problème de la gestion durable de la ressource en eau, face à sa raréfaction et à la nécessité de réduire les consommations, notamment en période de saison sèche. Elle consiste à développer un outil en ligne ergonomique et innovant permettant d’évaluer le potentiel de récupération d’eau de pluie et de dimensionner de manière optimale les cuves en fonction des besoins spécifiques des utilisateurs, tout en visualisant les économies réalisables de manière ludique et interactive. Cette solution s'adresse aux particuliers, aux établissements recevant du public (ERP), ainsi qu’aux partenaires techniques, en les sensibilisant à l’importance de la sobriété des usages et à l’intérêt de la récupération d’eau de pluie.

## Installation et Utilisation

### **Prérequis**
Avant de commencer, téléchargez les fichiers nécessaires, **Calcul_de_cuve** et **Catch_Water_app**. Les scripts Python suivants doivent être exécutés dans l'ordre indiqué :

#### 1. Exécuter le script `insertionPluviometrie.py`
Ce script permet d'insérer les données de pluviométrie dans la base de données en utilisant les données provenant d'un fichier `.xlsx`. Il charge et prépare les informations nécessaires avant d'insérer les valeurs dans le système.

#### 2. Exécuter le script `lecture_et_insertion_couts.py`
Ce script s'occupe de la lecture des coûts à partir de la source spécifiée et de leur insertion dans la base de données. Assurez-vous que toutes les données nécessaires sont présentes avant d'exécuter ce script.

#### 3. Exécuter le script `lecture_et_insertion_batient_et_adresse.py`
Ce script extrait les informations des patients et des adresses à partir des données sources (par exemple, un fichier Excel ou une autre base de données) et les insère dans le système.

#### 4. Exécuter l'application **app.py**

#### 5. Ouvrir un navigateur et aller sur: **127.0.0.1:5000**.

#### Ordre d'Exécution
1. Exécuter `insertionPluviometrie.py`
2. Exécuter `lecture_et_insertion_couts.py`
3. Exécuter `lecture_et_insertion_batient_et_adresse.py`
4. Exécuter `app.py`.
5. Ouvrir un navigateur et aller sur: **127.0.0.1:5000**.

#### Remarque
Dans le fichier `data_pluvios_2012-2022.xlsx`, les colonnes suivantes ont été supprimées :

- "dos d'ane"
- "l'ermitage cirad"
- "mare a vieille place"
- "pont d'yves"
- "riviere de l'est cirad"

## **Contributions**

Si vous souhaitez contribuer à ce projet, merci de suivre les [recommendations](/CONTRIBUTING.md).

## **Licence**

Le code est publié sous licence [MIT](/licence.MIT).

Les données référencés dans ce README et dans le guide d'installation sont publiés sous [Etalab Licence Ouverte 2.0](/licence.etalab-2.0).
