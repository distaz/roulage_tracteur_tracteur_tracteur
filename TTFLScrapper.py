# Ce script contient les fonctions permettant de lire les données du site ESPN afin de récupérer les données liées aux
# joueurs NBA
from lxml import html
import requests
import TTFLStats
from TTFLException import NoPosteError, NoPlayerError
from TTFLConstant import DICT_FRANCHISE
import re
from datetime import datetime, timedelta


def get_liste_joueurs(cd_franchise):
    """
    Cette fonction permet, pour une franchise donnée de récupérer les id des joueurs de cette franchise.
    :param cd_franchise: Le code de la franchise dont on veut la liste des joueurs
    :return: Les id des joueurs
    :rtype: set
    """
    # Initialisation du résultat
    joueurs = set()

    # Récupération de la liste des joueurs
    html_table_joueurs = html.fromstring(requests
                                         .get("https://www.espn.com/nba/team/roster/_/name/{}".format(cd_franchise))
                                         .content).find_class('Table__TR')

    # Parcours des lignes de la liste
    somme_team = 0
    for html_ligne in html_table_joueurs:
        for html_links in html_ligne.iterlinks():
            if html_links[1] == 'href':
                try:
                    somme_team += int(html_links[2].split("/")[7])
                    joueurs.add(html_links[2].split("/")[7])
                except ValueError:
                    pass
    print("\nChargement de la franchise : {}\n".format(cd_franchise))

    return joueurs


def get_stat_joueur(id_joueur, start_nba):
    """
    Cette fonction permet, pour un id joueur donné de renvoyer ses stats
    :param id_joueur: L'id du joueur dont on veut les stats
    :param start_nba: La date de début de saison en NBA
    :return: Les stats du joueur
    :rtype: Stats.StatsJoueur
    """
    # Initialisation du résultats
    joueur = TTFLStats.StatsJoueur()

    # Chargement du profil du joueur

    # Recuperation du code html de la page totale
    html_player_fullpage = html.fromstring(requests
                                           .get("http://www.espn.com/nba/player/gamelog/_/id/{}".format(id_joueur))
                                           .content)
    # Nom du joueur
    html_nom_joueur = html_player_fullpage.find_class('truncate')
    if len(html_nom_joueur) > 0:
        joueur.nom = "{} {}".format(html_nom_joueur[0].text_content(), html_nom_joueur[1].text_content())

    # Equipe et Poste du joueur
    html_equipe_joueur = html_player_fullpage.find_class('PlayerHeader__Team_Info')
    try:
        if len(html_equipe_joueur) > 0:
            joueur.equipe = html_equipe_joueur[0].text_content().split("#")[0]
            if html_equipe_joueur[0].text_content().find("Guard") > 0:
                joueur.poste = "Guard"
            elif html_equipe_joueur[0].text_content().find("Forward") > 0:
                joueur.poste = "Forward"
            elif html_equipe_joueur[0].text_content().find("Center") > 0:
                joueur.poste = "Center"
            else:
                raise NoPosteError("Aucun poste ne correspond pour {}".format(joueur))
    except NoPosteError:
        pass

    # Stats du match
    html_matchs_joueurs = html_player_fullpage.find_class('Table__TR')
    # Parcours de tous les matchs
    for html_stats_match in html_matchs_joueurs:
        iter_stat = html_stats_match.itertext()

        stat = iter_stat.__next__()
        # Si la ligne correspond à un match le premier élément est une date
        if re.match(r"[MTWFS][ouehra][neduit] [1-9][012]?/[1-9][0-9]?", stat) is not None:
            # Initialisation de la ligne de stat
            stats_match = TTFLStats.StatsMatch()

            # Date du match
            if int(stat.split(" ")[1].split("/")[0]) > 9 > datetime.now().month:
                stats_match.date = datetime(datetime.now().year - 1,
                                            int(stat.split(" ")[1].split("/")[0]),
                                            int(stat.split(" ")[1].split("/")[1]),
                                            0,
                                            0)
            else:
                stats_match.date = datetime(datetime.now().year,
                                            int(stat.split(" ")[1].split("/")[0]),
                                            int(stat.split(" ")[1].split("/")[1]),
                                            0,
                                            0)

            if stats_match.date < start_nba:
                continue

            # DOM/EXT
            stat = iter_stat.__next__()
            if stat == "vs":
                stats_match.lieu = "DOM"
            else:
                stats_match.lieu = "EXT"

            # Adversaire
            stat = iter_stat.__next__()
            stats_match.adversaire = DICT_FRANCHISE[stat]

            # Résultat match
            stat = iter_stat.__next__()
            if stat == "W":
                stats_match.resultat = "V"
            else:
                stats_match.resultat = "D"

            # Score match
            stat = iter_stat.__next__()
            if stats_match.lieu == "DOM":
                stats_match.score_pour = int(stat.split("-")[0])
                stats_match.score_contre = int(stat.split("-")[1].split(" ")[0])
            else:
                stats_match.score_pour = int(stat.split("-")[1].split(" ")[0])
                stats_match.score_contre = int(stat.split("-")[0])

            # Temps de jeu
            stat = iter_stat.__next__()
            stats_match.temps_jeu = int(stat)

            if stats_match.temps_jeu <= 0:
                continue

            # Tirs marques - Tirs tentes
            stat = iter_stat.__next__()
            stats_match.tirs_marques = int(stat.split("-")[0])
            stats_match.tirs_tentes = int(stat.split("-")[1])

            # 3pts marques - 3pts tentes
            iter_stat.__next__()
            stat = iter_stat.__next__()
            stats_match.troispts_marques = int(stat.split("-")[0])
            stats_match.troispts_tentes = int(stat.split("-")[1])

            # Lancers francs marques - Lancers francs tentes
            iter_stat.__next__()
            stat = iter_stat.__next__()
            stats_match.lances_marques = int(stat.split("-")[0])
            stats_match.lances_tentes = int(stat.split("-")[1])

            # Rebonds
            iter_stat.__next__()
            stat = iter_stat.__next__()
            stats_match.rebonds = int(stat)

            # Passes Décisives
            stat = iter_stat.__next__()
            stats_match.passes = int(stat)

            #  Blocs
            stat = iter_stat.__next__()
            stats_match.contres = int(stat)

            # Interceptions
            stat = iter_stat.__next__()
            stats_match.interceptions = int(stat)

            # Fautes
            stat = iter_stat.__next__()
            stats_match.fautes = int(stat)

            # Pertes de balles
            stat = iter_stat.__next__()
            stats_match.balles_perdues = int(stat)

            # Points
            stat = iter_stat.__next__()
            stats_match.points = int(stat)

            # Score TTFL
            stats_match.ttfl_score = int(stats_match.points
                                         + stats_match.rebonds
                                         + stats_match.passes
                                         + stats_match.contres
                                         + stats_match.interceptions
                                         + 2 * stats_match.lances_marques
                                         + 2 * stats_match.troispts_marques
                                         + 2 * stats_match.tirs_marques
                                         - stats_match.lances_tentes
                                         - stats_match.troispts_tentes
                                         - stats_match.tirs_tentes
                                         - stats_match.balles_perdues)

            # Ajout de la ligne de stat à la liste
            joueur.liste_matchs.append(stats_match)

    try:
        if joueur.nom != "":
            print(joueur)
            return joueur
        else:
            raise NoPlayerError("Le code {} ne donne pas accès à un joueur !".format(id_joueur))
    except NoPlayerError:
        print("Aucun joueur n'a été trouvé...")
        return TTFLStats.StatsJoueur()


def get_liste_match(nb_jour):
    """
    Fonction permettant de chercher les matchs qui vont avoir lieu entre aujourd'hui et un horizon en paramètre.
    :param nb_jour: Le nombre de jour à parcourir
    :return: Un dictionnaire contenant pour chaque date la liste des matchs du jour
    :rtype: dict
    """
    # Initialisation du résultat
    dico_matchs = dict()
    # Liste des dates de la périodes
    liste_date = [datetime(datetime.now().year, datetime.now().month, datetime.now().day) + timedelta(days=i)
                  for i in range(nb_jour)]

    # Chargement des matchs pour chaque jour
    for dt in liste_date:
        # Recuperation du code html de la page totale
        zero_bonus_jour = ""
        if dt.day < 10:
            zero_bonus_jour = "0"
        zero_bonus_mois = ""
        if dt.month < 10:
            zero_bonus_mois = "0"
        html_fullpage = html.fromstring(
            requests.get("https://www.espn.com/nba/schedule/_/date/{}{}{}{}{}"
                         .format(dt.year, zero_bonus_mois, dt.month, zero_bonus_jour, dt.day)).content)

        # Recperation de la liste des matchs du jour
        html_matchs = html_fullpage.find_class('responsive-table-wrap')[0]

        match_iterator = html_matchs.itertext()

        matchs_jour = []

        match = match_iterator.__next__()

        # Recuperation des matchs (DOM - EXT)
        while match is not None:
            if match in DICT_FRANCHISE.keys():
                ext = match
                match_iterator.__next__()
                match_iterator.__next__()
                match = match_iterator.__next__()
                dom = match
                # Ajout à la liste
                matchs_jour.append([DICT_FRANCHISE[dom], DICT_FRANCHISE[ext]])
            # Gestion de la fin de la boucle while
            try:
                match = match_iterator.__next__()
            except StopIteration:
                break
        dico_matchs[dt] = matchs_jour

    return dico_matchs
