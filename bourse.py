"""module bourse"""
import json
import requests
from datetime import datetime
from collections import defaultdict
from exceptions import ErreurDate


class Bourse:
    """class bourse"""
    def __init__(self):
        """méthode d'initialisation"""
        self.prix_actions = defaultdict(dict)

    def prix(self, symbole, dates):
        """méthode permettant le calcul du prix"""
        url = f'https://pax.ulaval.ca/action/{symbole}/historique/'
        params = {
            'début': "",
            'fin': dates,
        }

        results = requests.get(url=url, params=params, timeout=100)
        results = json.loads(results.text)

        if dates in results["historique"]:
            prix_ferm = results["historique"][dates]["fermeture"]
            return prix_ferm

        date_demandee = datetime.strptime(dates, '%Y-%m-%d').date()
        if datetime.now().date() < date_demandee:
            raise ErreurDate("Date postérieure à la date du jour.")

        dates_anterieures = [date for date in results['historique'] if date < dates]
        if dates_anterieures:
            date_recente_precedant = max(dates_anterieures)
            le_return = results["historique"][date_recente_precedant]["fermeture"]
            return le_return

        return 0.0

    def ajouter_prix(self, symbole, date, prix):
        """méthode avec attributs symbole, date et prix"""
        self.prix_actions[symbole][date] = prix
