import pandas as pd
from lxml import html
import requests
import re
import os
import datetime
import configparser
import numpy as np
import statsmodels.formula.api as sm

config = configparser.RawConfigParser()
config.read('./config.ini')

#Identifiants de connexion
PATH_TO_WRITE = config.get('csv', 'path')

# Le traitement ne s'effectue que si le fichier n'est pas a jour

FMAJ = False
EXI = os.path.exists("{}TTFL.csv".format(PATH_TO_WRITE))

if EXI:
    FMAJ = (datetime.date.fromtimestamp(os.path.getmtime("{}TTFL.csv".format(PATH_TO_WRITE))) == datetime.date.today() and datetime.datetime.fromtimestamp(os.path.getmtime("{}TTFL.csv".format(PATH_TO_WRITE))).hour > 8)
  
if not EXI or not FMAJ:
    
    TIME = datetime.datetime.now()
    
    #PARAMETRES GLOBAUX
    ANNEE = 2019
    START_NBA = datetime.date(ANNEE, 10, 22)
    END_NBA = datetime.date(ANNEE+1, 7, 1)
    DICT_FRANCHISE = dict()
    DICT_FRANCHISE["LAL"] = "Los Angeles Lakers"
    DICT_FRANCHISE["POR"] = "Portland Trail Blazers"
    DICT_FRANCHISE["DAL"] = "Dallas Mavericks"
    DICT_FRANCHISE["UTAH"] = "Utah Jazz"
    DICT_FRANCHISE["MIN"] = "Minnesota Timberwolves"
    DICT_FRANCHISE["CHI"] = "Chicago Bulls"
    DICT_FRANCHISE["SA"] = "San Antonio Spurs"
    DICT_FRANCHISE["WSH"] = "Washington Wizards"
    DICT_FRANCHISE["CLE"] = "Cleveland Cavaliers"
    DICT_FRANCHISE["DET"] = "Detroit Pistons"
    DICT_FRANCHISE["SAC"] = "Sacramento Kings"
    DICT_FRANCHISE["GS"] = "Golden State Warriors"
    DICT_FRANCHISE["DEN"] = "Denver Nuggets"
    DICT_FRANCHISE["IND"] = "Indiana Pacers"
    DICT_FRANCHISE["OKC"] = "Oklahoma City Thunder"
    DICT_FRANCHISE["BKN"] = "Brooklyn Nets"
    DICT_FRANCHISE["LAC"] = "LA Clippers"
    DICT_FRANCHISE["NO"] = "New Orleans Pelicans"
    DICT_FRANCHISE["MEM"] = "Memphis Grizzlies"
    DICT_FRANCHISE["BOS"] = "Boston Celtics"
    DICT_FRANCHISE["ATL"] = "Atlanta Hawks"
    DICT_FRANCHISE["NYK"] = "New York Knicks"
    DICT_FRANCHISE["NY"] = "New York Knicks"
    DICT_FRANCHISE["CHA"] = "Charlotte Hornets"
    DICT_FRANCHISE["MIL"] = "Milwaukee Bucks"
    DICT_FRANCHISE["PHI"] = "Philadelphia 76ers"
    DICT_FRANCHISE["MIA"] = "Miami Heat"
    DICT_FRANCHISE["PHX"] = "Phoenix Suns"
    DICT_FRANCHISE["ORL"] = "Orlando Magic"
    DICT_FRANCHISE["TOR"] = "Toronto Raptors"
    DICT_FRANCHISE["HOU"] = "Houston Rockets"
    
    
    ## Recuperation de la liste de joueurs 
    players = dict()
    
    tot_equipes = []
    tot_equipes.append("atl")
    tot_equipes.append("bos")
    tot_equipes.append("bkn")
    tot_equipes.append("cha")
    tot_equipes.append("chi")
    tot_equipes.append("cle")
    tot_equipes.append("dal")
    tot_equipes.append("den")
    tot_equipes.append("det")
    tot_equipes.append("gs")
    tot_equipes.append("hou")
    tot_equipes.append("ind")
    tot_equipes.append("lac")
    tot_equipes.append("lal")
    tot_equipes.append("mem")
    tot_equipes.append("mia")
    tot_equipes.append("mil")
    tot_equipes.append("min")
    tot_equipes.append("no")
    tot_equipes.append("ny")
    tot_equipes.append("okc")
    tot_equipes.append("orl")
    tot_equipes.append("phi")
    tot_equipes.append("phx")
    tot_equipes.append("por")
    tot_equipes.append("sac")
    tot_equipes.append("sa")
    tot_equipes.append("tor")
    tot_equipes.append("utah")
    tot_equipes.append("wsh")
    
    
    print("CHARGEMENT DE LA LISTE DES JOUEURS")
    for equipe in tot_equipes:
#    for equipe in ["tor"]:
        
        html_fullpage = html.fromstring(requests.get("https://www.espn.com/nba/team/roster/_/name/{}".format(equipe)).content)
        html_name = html_fullpage.find_class('Table__TBODY')
        for x in html_name:
            for t in x.iterlinks():
                if t[2][0:4] == "http":
                    players["{}/{}".format(t[2].split("/")[7], t[2].split("/")[8])] = 0
                    
    print("TERMINE !")
    
    
    dict_df = dict()
    
    ## Recuperation des stats des joueurs
    
    print("CHARGEMENT DES INFOS DES JOUEURS (Attention a ta connexion internet jeune fou ! )")
    for idp in players.keys():
#    for idp in ["3206/marc-gasol"]:    
        stat_player = []
        
        # Recuperation du code html de la page totale
        html_fullpage = html.fromstring(requests.get("http://www.espn.com/nba/player/gamelog/_/id/{}".format(idp)).content)

        #Recperation du nom du joueur
        player_name = ""
        if len(html_fullpage.find_class('truncate min-w-0')) > 0:
            player_name = "{} {}".format(html_fullpage.find_class('truncate min-w-0')[0].text_content(), html_fullpage.find_class('truncate min-w-0')[1].text_content())
            
        player_equipe = ""
        player_poste = ""
        if len(html_fullpage.find_class('PlayerHeader__Team_Info')) > 0:
            #Recperation de l'equipe du joueur + poste
            info_joueur = html_fullpage.find_class('PlayerHeader__Team_Info')[0].text_content()
            player_equipe = info_joueur.split("#")[0]
            if info_joueur.find("Guard") > 0:
                player_poste = "Guard"
            elif info_joueur.find("Forward") > 0:
                player_poste = "Forward"
            elif info_joueur.find("Center") > 0:
                player_poste = "Center"
            else :
                print("ERREUR POSTE : {}".format(info_joueur))
            
        print("{} ({})".format(player_name, player_equipe))
        
        
        # Recuperation du code html du tableau de stat + Init de l'iterator
        tab_html_tabstat = html_fullpage.find_class('Table__TBODY')
        
#        for html_tabstat in tab_html_tabstat:
        if len(tab_html_tabstat) > 0:
            html_tabstat = tab_html_tabstat[0]
            stat_iterator = html_tabstat.itertext()
                
            # Tant que stat est renseigne on boucle pour trouver tous les matchs
            stat = stat_iterator.__next__()
            
            while stat is not None:
                
                # Recherche d'un champ date pour initialiser la ligne
                if re.match(r"[MTWFS][ouehra][neduit] [1-9][012]?/[1-9][0-9]?", stat) is not None:
        
                    # Creation de la ligne de stat
                    stat_match = [player_name, player_equipe, player_poste]
                    
                    # Info num 1 : date du match
                    mois = int(stat.split(" ")[1].split("/")[0])
                    jour = int(stat.split(" ")[1].split("/")[1])
                    
                    if mois > 9:
                        stat_match.append(datetime.date(ANNEE, mois, jour))
                    else:
                        stat_match.append(datetime.date(ANNEE + 1, mois, jour))
                       
                    # Info num 2 : DOM/EXT
                    stat = stat_iterator.__next__()
                    if stat == "vs" :
                        stat_match.append("DOM")
                    else :
                        stat_match.append("EXT")
                        
                    # Info num 3 : Adversaire
                    stat = stat_iterator.__next__()    
                    if stat in DICT_FRANCHISE:
                        stat_match.append(DICT_FRANCHISE[stat])
                    else :
                        stat_match.append("Equipe Etrangere")  
                                
                        
                    # Info num 4 : V/D
                    stat = stat_iterator.__next__()
                    if re.match(r"[0-9]?[0-9]?[0-9]?-[0-9]?[0-9]?[0-9]?", stat) is None:
                        if stat == "W":
                            stat_match.append("V")
                        else :
                            stat_match.append("D")
                        
                    # Info num 5 : Resultats du match
                        stat = stat_iterator.__next__()
                    else :
                        stat_match.append("P")
                    if stat_match[4] == "DOM" :
                        stat_match.append(int(stat.split("-")[0]))
                        stat_match.append(int(stat.split("-")[1].split(" ")[0]))
                    else :
                        stat_match.append(int(stat.split("-")[1].split(" ")[0]))
                        stat_match.append(int(stat.split("-")[0]))
                        
                        
                    # Info num 6 : Temps de jeu
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat))
                        
                    # Info num 7 : Tirs marques - Tirs tentes
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat.split("-")[0]))
                    stat_match.append(int(stat.split("-")[1]))
                        
                    # Info num 8 : 3pts marques - 3pts tentes
                    stat = stat_iterator.__next__()
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat.split("-")[0]))
                    stat_match.append(int(stat.split("-")[1]))
                        
                    # Info num 9 : Lancers francs marques - Lancers francs tentes
                    stat = stat_iterator.__next__()
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat.split("-")[0]))
                    stat_match.append(int(stat.split("-")[1]))
                        
                    # Info num 10 : Rebonds
                    stat = stat_iterator.__next__()
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat))
                        
                    # Info num 11 : Passes Decisives
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat))
                        
                    # Info num 12 : Blocs
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat))
                        
                    # Info num 13 : Interceptions
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat))
                        
                    # Info num 14 : Fautes
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat))
                        
                    # Info num 15 : Pertes de balles
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat))
                        
                    # Info num 16 : Points
                    stat = stat_iterator.__next__()
                    stat_match.append(int(stat))
                        
                    # Info num 17 : Score TTFL
                    stat_match.append(int(stat_match[22] 
                                    + stat_match[16] 
                                    + stat_match[17] 
                                    + stat_match[19] 
                                    + stat_match[18] 
                                    + 2 * stat_match[10] 
                                    + 2 * stat_match[12] 
                                    + 2 * stat_match[14] 
                                    - stat_match[11] 
                                    - stat_match[13] 
                                    - stat_match[15] 
                                    - stat_match[21]))
                    
                    stat_player.append(stat_match)
                                        
                try :
                    stat = stat_iterator.__next__()
                except StopIteration:
                    break
            
                
        #Creation du DATA_FRAME du joueur
        
        #Creation des labels
        noms_colonnes = ["joueur",
                         "equipe",
                         "poste",
                         "date_match",
                         "lieu",
                         "adversaire",
                         "statut",
                         "score_pour",
                         "score_contre",
                         "min",
                         "fgm",
                         "fga",
                         "3pm",
                         "3pa",
                         "ftm",
                         "fta",
                         "reb",
                         "ast",
                         "blk",
                         "stl",
                         "pf",
                         "tov",
                         "pts",
                         "ttfl"]
        
        player_df = pd.DataFrame.from_records(stat_player, columns=noms_colonnes)
        
        # Choix des matchs NBA uniquement 
        player_df = player_df[player_df["date_match"] >= START_NBA]
        player_df = player_df[player_df["date_match"] <= END_NBA]
        player_df = player_df[["joueur", "poste", "date_match", "equipe", "adversaire", "lieu", "min", "ttfl"]]
        
        if not player_df.empty:
            dict_df[idp] = player_df
    print("CHARGEMENT TERMINE")    
    
    all_nba_stat = pd.concat(list(map(lambda x : dict_df[x], dict_df.keys())))
            
    
    print("CALCUL DES MOYENNES GLISSANTES")
    
    #enleve la ligne si le joueur n'a pas joue
    all_nba_stat = all_nba_stat[all_nba_stat["min"] >= 0]
    all_nba_stat = all_nba_stat.reset_index(drop = True)
    
    END_EXTRACT = datetime.datetime.now()
    
    
    
    # Calcul de TTFL_30 : moyenne ttfl glissante sur 30 jours
    all_nba_stat["ttfl_30"] = np.nan
    for date in [datetime.date.today() - datetime.timedelta(days=x) for x in range(0, (datetime.date.today() - START_NBA).days + 1)]:
        nba_red_date = all_nba_stat[["joueur", "ttfl"]]
        nba_red_date = nba_red_date[all_nba_stat["date_match"] <= date]
        nba_red_date = nba_red_date[all_nba_stat["date_match"] > date - datetime.timedelta(days=30)]
        nba_red_date = nba_red_date.groupby("joueur").mean()
        nba_red_date = nba_red_date.reset_index(level=['joueur'])
        nba_red_date["date_match"] = date
        nba_red_date = nba_red_date.rename(index = str, columns={"ttfl" : "ttfl_30"})
    
        
        all_nba_stat = pd.merge(all_nba_stat, nba_red_date, how = 'left', on= ["joueur", "date_match"])
        all_nba_stat["ttfl_30"] = [all_nba_stat["ttfl_30_y"][i] if all_nba_stat["ttfl_30_x"].isnull()[i] else all_nba_stat["ttfl_30_x"][i] for i in range(len(all_nba_stat["ttfl_30_x"]))]
        all_nba_stat = all_nba_stat[["joueur", "poste", "date_match", "adversaire", "equipe", "lieu", "ttfl", "ttfl_30"]]
    
    END_GLISS = datetime.datetime.now()
    print("CALCUL TERMINE")
    
    
    
    
    
    # Calcul de TTFL_30 : moyenne ttfl glissante sur 10 jours
    all_nba_stat["ttfl_10"] = np.nan
    for date in [datetime.date.today() - datetime.timedelta(days=x) for x in range(0, (datetime.date.today() - START_NBA).days + 1)]:
        nba_red_date = all_nba_stat[["joueur", "ttfl"]]
        nba_red_date = nba_red_date[all_nba_stat["date_match"] <= date]
        nba_red_date = nba_red_date[all_nba_stat["date_match"] > date - datetime.timedelta(days=10)]
        nba_red_date = nba_red_date.groupby("joueur").mean()
        nba_red_date = nba_red_date.reset_index(level=['joueur'])
        nba_red_date["date_match"] = date
        nba_red_date = nba_red_date.rename(index = str, columns={"ttfl" : "ttfl_10"})
    
        
        all_nba_stat = pd.merge(all_nba_stat, nba_red_date, how = 'left', on= ["joueur", "date_match"])
        all_nba_stat["ttfl_10"] = [all_nba_stat["ttfl_10_y"][i] if all_nba_stat["ttfl_10_x"].isnull()[i] else all_nba_stat["ttfl_10_x"][i] for i in range(len(all_nba_stat["ttfl_10_x"]))]
        all_nba_stat = all_nba_stat[["joueur", "poste", "date_match", "adversaire", "equipe", "lieu", "ttfl", "ttfl_30", "ttfl_10"]]
    
    END_GLISS = datetime.datetime.now()
    print("CALCUL TERMINE")
    
    ##Prise en compte des blesses 
    
    
    #otre_fr = {"Los Angeles Clippers" : "LA Clippers", }
    #
    #html_fullpage = html.parse("http://www.rotoworld.com/teams/injuries/nba/all/").getroot()
    #
    ##Recperation du nom du joueur
    #html_name = html_fullpage.find_class('left_wide')[0]
    #
    #blesus_iterator = html_name.itertext()
    #
    #CURRENT_FR = ""
    #liste_blesse = []
    #
    #test = True
    #while test :
    #    try :
    #        stat = blesus_iterator.__next__()
    #        if re.match(r"[A-Z.a-z']+? ([0-9A-Z.a-z-' ]+?){1,}", stat) is not None:
    #            if stat in DICT_FRANCHISE.values() or stat in otre_fr.keys():
    #                CURRENT_FR = stat
    #                if stat in otre_fr.keys():
    #                    CURRENT_FR = otre_fr[stat]
    #            else :
    #                check = 0
    #                for x in ["Injury", "knee", "trade", "miss", "assigned", "injury", "schedule", "travel", "questionable", "interested", "starting", "sidelines", "coach", "player", "indefinitely", "out", "play", "doubtful", "traded", "Out", "suffered", "According", "return", "ankle", "days", "re-evaluated", "hopeful", "diagnosed", "back", "left", "right", "night", "season", "Targeting", "week", "weeks"]:
    #                    if x in stat.split(" "):
    #                        check = 1
    #                if check == 0 :
    #                     noms_colonnes = ["joueur",
    #                                      "equipe",
    #                                      "blesse"]
    #                     player_blesse = pd.DataFrame.from_records([[stat, CURRENT_FR, 1]], columns=noms_colonnes)
    #                     liste_blesse.append(player_blesse)  
    #    except StopIteration:
    #        test = False
    #    
    #
    #for i in range(len(liste_blesse)):
    #    if i == 0:
    #        blesse_nba = liste_blesse[0]
    #    else:
    #        blesse_nba = blesse_nba.append(liste_blesse[i], ignore_index=True)
    #
    #
    #all_nba_stat = pd.merge(all_nba_stat, blesse_nba, how = 'left', on= ["joueur", "equipe"])
    #all_nba_stat["blesse"] = [0 if all_nba_stat["blesse"].isnull()[i] else 1 for i in range(len(all_nba_stat["blesse"]))]
    
    
    
    
    print("Temps pour importer les donnees : {}".format(END_EXTRACT - TIME))
    print("Temps pour calculer les moyennes glissantes : {}".format(END_GLISS - END_EXTRACT))
    print("Nombre de joueurs importes : {}".format(len(dict_df)))
    
    print("CHARGEMENT DU CALENDRIER")
    # Creation des dates des 30 prochains jours
    DATE_JOUR = datetime.date.today()
    LIST_DATE = []
    # LECTURE DU PARAMETRE POUR LE NB DE JOURS PREDITS
    NB_JOURS_PREDITS = int(config.get('predict', 'nbdays'))
    ##################et optimiser sur 10 jours au lieu de 30
    #############################################
    for i in range(NB_JOURS_PREDITS) :
        temp_date = DATE_JOUR + datetime.timedelta(days = i)
        mo = "0{}".format(temp_date.month)[-2:]
        da = "0{}".format(temp_date.day)[-2:]
        LIST_DATE.append("{}{}{}".format(temp_date.year, mo, da))
    
    
    dico_matchs = dict()
    
    # Chargement des matchs pour chaque jour
    for dt in LIST_DATE:
        
        # Recuperation du code html de la page totale
        html_fullpage = html.fromstring(requests.get("http://www.espn.com/nba/schedule/_/date/{}".format(dt)).content)
        
        #Recperation de la liste des matchs du jour
        html_matchs = html_fullpage.find_class('responsive-table-wrap')[0]
        
        match_iterator = html_matchs.itertext()
        
        matchs_jour = []
        
        match = match_iterator.__next__()
        
        # Recuperation des matchs (DOM - EXT)
        while match is not None:
            
            
            if match in DICT_FRANCHISE.keys():
                ext = match
                match = match_iterator.__next__()
                match = match_iterator.__next__()
                match = match_iterator.__next__()
                dom = match
                
                matchs_jour.append([DICT_FRANCHISE[dom], DICT_FRANCHISE[ext]])
            
            try :
                match = match_iterator.__next__()
            except StopIteration:
                break 
        dico_matchs[dt] = matchs_jour
#        print(matchs_jour)
            
    #print(dico_matchs)
    print("CALENDRIER OK")
        
    
    print("TRUCS CHELOU DE MARCO")
    players_teams=[[],[],[],[],[]]
    
    for i in range(1,len(all_nba_stat['joueur'])):
        if all_nba_stat['joueur'][i-1]!=all_nba_stat['joueur'][i] or i==1:
            players_teams[0].append(all_nba_stat['joueur'][i])
            players_teams[1].append(all_nba_stat['equipe'][i])
            players_teams[2].append(all_nba_stat['poste'][i])
            players_teams[3].append(all_nba_stat['ttfl_30'][i])
            players_teams[4].append(all_nba_stat['ttfl_10'][i])
    
    
    calendars=dict() 
    #creation du calendrier avec les joueurs impliques a chaque date
    for date in dico_matchs:
        players=[]
        for game in dico_matchs[date]:
            teamH=game[0]
            teamA=game[1]
            for i in range(len(players_teams[1])):
                if players_teams[1][i]==teamH:
                    player=[]
                    player.append(players_teams[0][i])
                    player.append(teamA)
                    player.append(players_teams[2][i])
                    player.append("DOM")
                    player.append(players_teams[3][i])
                    players.append(player)
                    player.append(players_teams[4][i])
                elif players_teams[1][i]==teamA:
                    player=[]
                    player.append(players_teams[0][i])
                    player.append(teamH)
                    player.append(players_teams[2][i])
                    player.append("EXT")
                    player.append(players_teams[3][i])
                    players.append(player)
                    player.append(players_teams[4][i])
            
        calendars[date]=players
    
    
    data=all_nba_stat[['joueur','adversaire','lieu','poste','ttfl','ttfl_30','ttfl_10']]
    
    #bonus calcule directement dans la regression
    reg_30=sm.ols(formula="ttfl~lieu+adversaire*poste+ttfl_30",data=data).fit()
    reg_10=sm.ols(formula="ttfl~lieu+adversaire*poste+ttfl_10",data=data).fit()
    print(reg_30.rsquared_adj)
    print(reg_10.rsquared_adj)
    
    matrix=np.zeros((len(all_nba_stat.groupby(['joueur'])),len(calendars)))
    noms=[]
    
    #remplissage de la matrice exp_points par joueur par date
    i=0
    for joueur in all_nba_stat.groupby(['joueur']):
        j=0
        noms.append(joueur[0])
        for date in calendars:
            df_j=pd.DataFrame(calendars[date],columns=['joueur','adversaire','poste','lieu','ttfl_30','ttfl_10']).set_index('joueur')
            df=pd.DataFrame(calendars[date],columns=['joueur','adversaire','poste','lieu','ttfl_30','ttfl_10'])
            if joueur[0] in df_j['lieu']:
                matrix[i,j]=reg_30.predict(df.iloc[np.where(df['joueur']==joueur[0])])/2+reg_10.predict(df.iloc[np.where(df['joueur']==joueur[0])])/2
            j+=1
        i+=1
    
    dates=[]
    for date in calendars:
        dates.append(date[0:4]+"-"+date[4:6]+"-"+date[6:8])
    
    noms=pd.DataFrame(noms)
    dates=pd.DataFrame(dates)
    
    print("FIN DES TRUCS CHELOU DE MARCO")
    
    print("ECRITURE DES CSV")
    np.savetxt("{}TTFL.csv".format(PATH_TO_WRITE), matrix, delimiter=",")
    np.savetxt("{}noms.csv".format(PATH_TO_WRITE),noms,fmt="%s")
    np.savetxt("{}calendrier.csv".format(PATH_TO_WRITE),dates,fmt="%s")
