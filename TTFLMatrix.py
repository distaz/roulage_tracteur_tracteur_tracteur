# Ce script permet de récupérer les données des joueurs NBA
# En sortie, il y a un fichier csv qui contient les prédictions pour les jours à venir
import os
from datetime import datetime, date, timedelta
import configparser

import pandas as pd
import numpy as np
import statsmodels.formula.api as sm

import TTFLScrapper as ttfls
from TTFLConstant import START_NBA, CD_FRANCHISES

# Configuration :
config = configparser.RawConfigParser()
config.read("./config.ini")
PATH_TO_WRITE = config.get('csv', 'path')  # Identifiants de connexion
NB_JOURS_PREDITS = int(config.get('predict', 'nbdays'))  # Nombre de jours à prédire

# Le traitement ne s'effectue que si le fichier n'est pas à jour
EXI = os.path.exists("{}/TTFL.csv".format(PATH_TO_WRITE))
if EXI:
    FMAJ = (date.fromtimestamp(os.path.getmtime(
        "{}/TTFL.csv".format(PATH_TO_WRITE))) == date.today() and datetime.fromtimestamp(
        os.path.getmtime("{}/TTFL.csv".format(PATH_TO_WRITE))).hour > 8)
else:
    FMAJ = False

START_TIME = datetime.now()
if not EXI or not FMAJ:

    if not os.path.exists("{}/all_nba_stat.csv".format(PATH_TO_WRITE)):
        print("Début du chargement des joueurs :")
        all_nba_stat = pd.concat([ttfls.get_stat_joueur(idjoueur, START_NBA).to_dataframe(columns=["Nom",
                                                                                                   "Poste",
                                                                                                   "Date",
                                                                                                   "Adversaire",
                                                                                                   "Equipe",
                                                                                                   "Lieu",
                                                                                                   "TTFL"])
                                  for equipe in CD_FRANCHISES
                                  for idjoueur in ttfls.get_liste_joueurs(equipe)],
                                 sort=False).reset_index(drop=True)
        NB_JOUEURS_MANQUES = len(all_nba_stat[all_nba_stat["Nom"] == ""])
        END_EXTRACT = datetime.now()
        print("\nLe chargement des joueurs est terminé !")
    
        # Calcul des moyennes glissantes
        def calcul_moyenne_glissante(df_stat, nb_jour):
            iter_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
            df_stat["TTFL_{}".format(nb_jour)] = np.nan
            while iter_date > START_NBA:
                nba_red_date = df_stat[df_stat["Date"] < iter_date]
                nba_red_date = nba_red_date[nba_red_date["Date"] >= iter_date - timedelta(days=nb_jour)]
                nba_red_date = nba_red_date.filter(["Nom", "TTFL"], axis=1).groupby("Nom").mean().reset_index()
                nba_red_date["Date"] = iter_date
                nba_red_date = nba_red_date.rename(columns={"TTFL": "TTFL_{}".format(nb_jour)})
                df_stat = pd.merge(df_stat, nba_red_date, how='left', on=["Nom", "Date"], suffixes=["", "_new"])
                df_stat["TTFL_{}".format(nb_jour)].fillna(df_stat["TTFL_{}_new".format(nb_jour)], inplace=True)
                df_stat.drop(["TTFL_{}_new".format(nb_jour)], axis=1, inplace=True)
                iter_date -= timedelta(days=1)
            return df_stat
        all_nba_stat = calcul_moyenne_glissante(all_nba_stat, 30)
        all_nba_stat = calcul_moyenne_glissante(all_nba_stat, 10)
        all_nba_stat.to_csv("{}/all_nba_stat.csv".format(PATH_TO_WRITE), sep=";")
    else:
        all_nba_stat = pd.read_csv("{}/all_nba_stat.csv".format(PATH_TO_WRITE), sep=";")

    END_GLISS = datetime.now()

    # Chargemet du calendrier
    print("\nChargement du calendrier en cours...")
    dico_matchs = ttfls.get_liste_match(NB_JOURS_PREDITS)
    print("Fin du chargement")

    print("\nCalcul des prédictions...")

    # On garde que la dernière ligne de chaque joueur
    all_nba_stat.sort_values(["Equipe", "Nom", "Date"], ascending=[True, True, False])
    last_nba_stat = all_nba_stat.groupby("Nom").first().reset_index().drop(["Adversaire", "Lieu"], axis=1)

    # Remplissage du calendrier avec les joueurs qui vont jouer chaque match
    calendars = dict()
    for dt in dico_matchs.keys():
        calendars[dt] = []
        for match in dico_matchs[dt]:
            df_dom = last_nba_stat[last_nba_stat["Equipe"] == match[0]]
            df_dom["Adversaire"] = match[1]
            df_dom["Lieu"] = "DOM"
            df_ext = last_nba_stat[last_nba_stat["Equipe"] == match[1]]
            df_ext["Adversaire"] = match[0]
            df_ext["Lieu"] = "EXT"
            calendars[dt].append(pd.concat([df_dom, df_ext], sort=False)
                                 .reset_index()
                                 .filter(["Nom", "Adversaire", "Poste", "Lieu", "TTFL_30", "TTFL_10"]))
        calendars[dt] = pd.concat(calendars[dt], sort=False)

    # Calcul du modèle
    data = all_nba_stat[['Nom', 'Adversaire', 'Lieu', 'Poste', 'TTFL', 'TTFL_30', 'TTFL_10']]

    # Bonus calculé directement dans la régression
    reg_30 = sm.ols(formula="TTFL~Lieu+Adversaire*Poste+TTFL_30", data=data).fit()
    print("    R² du modèle avec TTFL_30 : {}".format(reg_30.rsquared_adj))
    reg_10 = sm.ols(formula="TTFL~Lieu+Adversaire*Poste+TTFL_10", data=data).fit()
    print("    R² du modèle avec TTFL_10 : {}".format(reg_10.rsquared_adj))

    # Remplissage de la matrice contenant les prédictions
    df_matrix = pd.DataFrame(last_nba_stat["Nom"]).set_index("Nom")
    for dt in calendars.keys():
        df_matrix[dt] = 0
    
    for dt in df_matrix.columns:
        for joueur in df_matrix.index:
            # noinspection PyTypeChecker
            if len(calendars[dt][calendars[dt]["Nom"] == joueur]) > 0:
                # noinspection PyTypeChecker,PyTypeChecker
                df_matrix.loc[joueur, dt] = float(reg_30.predict(calendars[dt][calendars[dt]["Nom"] == joueur])) / 2 + \
                                            float(reg_10.predict(calendars[dt][calendars[dt]["Nom"] == joueur])) / 2
        
    # Ecriture du csv
    print("Prédictions terminées => Ecriture dans le fichier csv.")
    df_matrix.to_csv("{}/TTFL.csv".format(PATH_TO_WRITE), sep=";")
    END_EXEC = datetime.now()

    # Résumé de l'éxécution 
    print("\n\n------------------------------------------------------------------------------------------\n"
          "Temps pour importer les données : {}".format(END_EXTRACT - START_TIME))
    print("Temps pour calculer les moyennes glissantes : {}".format(END_GLISS - END_EXTRACT))
    print("Nombre de joueurs importés : {}".format(len(all_nba_stat["Nom"].drop_duplicates())))
    print("Nombre de joueurs passés à la trappe : {}".format(NB_JOUEURS_MANQUES))
    print("Soit un total de {} lignes de stat !".format(len(all_nba_stat)))
    print("Les prédictions sont faites pour les {} prochains matchs !".format(NB_JOURS_PREDITS))
    print("\nTemps total d'éxécution : {}".format(END_EXEC - START_TIME))
