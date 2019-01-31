# roulage_tracteur_tracteur_tracteur
Algo pour rouler sur des mères avec des tracteurs


# UTILISATION DU SCRIPT

La variable d'environement PATH doit être configuré au préalable afin que la console puisse acceder aux programmes R et Python.

********* TEST *********
- Lancez la console 
- Testez si votre terminal connait python et R. Lancez la commande suivante :
____________________________________________________________________
python 
____________________________________________________________________
- Si cela fonctionne vous devez avoir quelque chose de ce genre là :
____________________________________________________________________
C:\Users\quent>python
Python 3.6.2 (v3.6.2:5fd33b5, Jul  8 2017, 04:57:36) [MSC v.1900 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
____________________________________________________________________
Il faut alors quitter python avec la commande :
____________________________________________________________________
quit()
____________________________________________________________________
- Si cela ne fonctionne pas et qu'il vous dit :
____________________________________________________________________
C:\Users\quent>python
'python' n’est pas reconnu en tant que commande interne
ou externe, un programme exécutable ou un fichier de commandes.
____________________________________________________________________
Alors, il faut ajouter python à votre variable d'environnement PATH (Voir ci-dessous)

- Il faut faire la même chose pour R:
____________________________________________________________________
R
____________________________________________________________________
- Si cela fonctionne vous devez avoir quelque chose de ce genre là :
____________________________________________________________________
C:\Users\quent>R

R version 3.5.2 (2018-12-20) -- "Eggshell Igloo"
Copyright (C) 2018 The R Foundation for Statistical Computing
Platform: x86_64-w64-mingw32/x64 (64-bit)

R est un logiciel libre livré sans AUCUNE GARANTIE.
Vous pouvez le redistribuer sous certaines conditions.
Tapez 'license()' ou 'licence()' pour plus de détails.

R est un projet collaboratif avec de nombreux contributeurs.
Tapez 'contributors()' pour plus d'information et
'citation()' pour la façon de le citer dans les publications.

Tapez 'demo()' pour des démonstrations, 'help()' pour l'aide
en ligne ou 'help.start()' pour obtenir l'aide au format HTML.
Tapez 'q()' pour quitter R.

>
____________________________________________________________________
Il faut alors quitter R avec la commande :
____________________________________________________________________
q()
____________________________________________________________________
- Si cela ne fonctionne pas et qu'il vous dit :
____________________________________________________________________
C:\Users\quent>R
'R' n’est pas reconnu en tant que commande interne
ou externe, un programme exécutable ou un fichier de commandes.
____________________________________________________________________
Alors, il faut ajouter R à votre variable d'environnement PATH (Voir ci-dessous)

- Afin d'ajouter python et R a votre variable d'environnement

*** SOUS WINDOWS 10 ***
Tapez dans votre recherche Windows "Système".
Une fenêtre s'ouvre. Cliquez sur "Afficher les paramètres système avancés".
Une fenêtre s'ouvre. Cliquez sur "Variables d'environnement..."
Selectionnez "Path" puis faites "Modifier".
Cliquez sur "Nouveau" puis ajouter les chemins de R et python. 
Exemple de mes chemins :
- Pour python : "C:\Users\quent\AppData\Local\Programs\Python\Python36\" ou "C:\User\quent\Anaconda 3"
- Pour R : "C:\Program Files\R\R-3.5.2\bin"







