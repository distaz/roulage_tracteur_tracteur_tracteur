"""
Stats class
~~~~~~~~~~~

Stat est une libraririe contenant des classes permettant de stocker les stats de basket.
"""
import datetime
import pandas as pd


class StatsJoueur(object):
    """
    Classe contenant les attributs d'un joueur :
    - Nom
    - Poste
    - Equipe
    - Liste des matchs
    """
    def __init__(self):
        """
        Constructeur de la classe StatsJoueur
        """
        self.nom = ""
        self.equipe = ""
        self.poste = ""
        self.liste_matchs = []

    def __str__(self):
        """
        Objet to string
        """
        return "{} ({}) - {}".format(self.nom, self.poste, self.equipe)

    def __repr__(self):
        """
        Objet to string
        """
        return "{} ({}) - {}".format(self.nom, self.poste, self.equipe)

    def to_dataframe(self, columns):
        return pd.DataFrame({"Nom": [self.nom] * len(self.liste_matchs),
                             "Equipe": [self.equipe] * len(self.liste_matchs),
                             "Poste": [self.poste] * len(self.liste_matchs),
                             "Date": [tmp.date for tmp in self.liste_matchs],
                             "Lieu": [tmp.lieu for tmp in self.liste_matchs],
                             "Adversaire": [tmp.adversaire for tmp in self.liste_matchs],
                             "Resultat": [tmp.resultat for tmp in self.liste_matchs],
                             "PtsPour": [tmp.score_pour for tmp in self.liste_matchs],
                             "PtsContre": [tmp.score_contre for tmp in self.liste_matchs],
                             "Temps": [tmp.temps_jeu for tmp in self.liste_matchs],
                             "FGM": [tmp.tirs_marques for tmp in self.liste_matchs],
                             "FGA": [tmp.tirs_tentes for tmp in self.liste_matchs],
                             "3PM": [tmp.troispts_marques for tmp in self.liste_matchs],
                             "3PA": [tmp.troispts_tentes for tmp in self.liste_matchs],
                             "LFM": [tmp.lances_marques for tmp in self.liste_matchs],
                             "LMA": [tmp.lances_tentes for tmp in self.liste_matchs],
                             "REB": [tmp.rebonds for tmp in self.liste_matchs],
                             "PD": [tmp.passes for tmp in self.liste_matchs],
                             "BLK": [tmp.contres for tmp in self.liste_matchs],
                             "STL": [tmp.interceptions for tmp in self.liste_matchs],
                             "TOV": [tmp.balles_perdues for tmp in self.liste_matchs],
                             "PTS": [tmp.points for tmp in self.liste_matchs],
                             "Faute": [tmp.fautes for tmp in self.liste_matchs],
                             "TTFL":  [tmp.ttfl_score for tmp in self.liste_matchs]})\
            .filter(columns, axis=1)


class StatsMatch(object):
    """
    Classe contenant les stats d'un joueur pour un match :
    - Date
    - Lieu
    - Adversaire
    - Résultat (V/D)
    - Score Pour
    - Score Contre
    - Temps de jeu
    - Tirs marqués
    - Tirs tentés
    - 3pts marqués
    - 3pts tentés
    - Lancers francs marqués
    - Lancers francs tentés
    - Rebonds
    - Passes Décisives
    - Blocs
    - Interceptions
    - Fautes
    - Pertes de balles
    - Points
    - Score TTFL
    """
    def __init__(self):
        """
        Constructeur de la classe StatsMatch
        """
        self.date = datetime.datetime.now()
        self.lieu = ""
        self.adversaire = ""
        self.resultat = ""
        self.score_pour = 0
        self.score_contre = 0
        self.temps_jeu = 0
        self.tirs_tentes = 0
        self.tirs_marques = 0
        self.lances_tentes = 0
        self.lances_marques = 0
        self.troispts_tentes = 0
        self.troispts_marques = 0
        self.rebonds = 0
        self.passes = 0
        self.contres = 0
        self.interceptions = 0
        self.balles_perdues = 0
        self.fautes = 0
        self.points = 0
        self.ttfl_score = 0

    def __str__(self):
        """
        Objet to string
        """
        return "{} contre {} ({} - {})\n  {}min : {} pts - {} rebonds - {} passes\n  TTFL : {} pts"\
            .format(self.resultat,
                    self.adversaire,
                    self.score_pour,
                    self.score_contre,
                    self.temps_jeu,
                    self.points,
                    self.rebonds,
                    self.passes,
                    self.ttfl_score)

    def __repr__(self):
        """
        Objet to string
        """
        return "\n{} contre {} à {} ({} - {})\n  {}min : {} pts ({}/{} = {:2.1%} - {:2.1%} - {:2.1%}) - {} rebonds" \
               " - {} passes - {} blocks - {} interceptions - {} turnover - {} fautes\n  TTFL : {} pts\n"\
            .format(self.resultat,
                    self.adversaire,
                    self.lieu,
                    self.score_pour,
                    self.score_contre,
                    self.temps_jeu,
                    self.points,
                    self.tirs_marques,
                    self.tirs_tentes,
                    self.tirs_marques / self.tirs_tentes if self.tirs_tentes > 0 else 0,
                    self.troispts_marques / self.troispts_tentes if self.troispts_tentes > 0 else 0,
                    self.lances_marques / self.lances_tentes if self.lances_tentes > 0 else 0,
                    self.rebonds,
                    self.passes,
                    self.contres,
                    self.interceptions,
                    self.balles_perdues,
                    self.fautes,
                    self.ttfl_score)
