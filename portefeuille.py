"""Module Portefeuilles"""
import os
import json
import io
from datetime import datetime, timedelta
from exceptions import ErreurDate, ErreurQuantité, LiquiditéInsuffisante
import matplotlib.pyplot as plt
import numpy as np

class Portefeuille:
    """Classe portefeuille."""
    def __init__(self, bourse, nom_portefeuille=None):
        """Initialisation du portefeuille."""
        self.bourse = bourse
        self.nom_portefeuille = nom_portefeuille
        self.liquidites = 0
        self.actions = {}
        self.transactions = []
        self.charger_portfolio()

    def charger_portfolio(self):
        """Charge les données du portefeuille depuis un fichier."""
        try:
            with io.open(
                os.path.join(f'{self.nom_portefeuille}.json'), 'r', encoding='utf-8'
                ) as file:
                data = json.load(file)
                self.liquidites = data.get('liquidites', 0)
                self.actions = data.get('actions', {})
        except FileNotFoundError:
            self.liquidites = 0
            self.actions = {}

    def sauvegarder_portfolio(self):
        """Sauvegarde les données du portefeuille dans un fichier."""
        data = {'liquidites': self.liquidites, 'actions': self.actions}
        with io.open(os.path.join(f'{self.nom_portefeuille}.json'), 'w', encoding='utf-8') as file:
            json.dump(data, file)

    def valider_date(self, date):
        """Méthode pour vérifier la validité des dates"""
        if date > datetime.now().date():
            raise ErreurDate("La date spécifiée est postérieure à la date du jour.")
    def enregistrer_transaction(self, type_transaction, montant, date):
        """Méthode pour enregistrer les transactions"""
        self.transactions.append({'type': type_transaction, 'montant': montant, 'date': date})

    def deposer(self, montant, date=None):
        """Méthode pour augmenter solde"""
        date = date or datetime.now().date()
        self.valider_date(date)
        self.liquidites += montant
        self.enregistrer_transaction('Dépôt', montant, date)

    def solde(self, date=None):
        """Méthode pour indiquer solde"""
        date = date or datetime.now().date()
        self.valider_date(date)
        return self.liquidites

    def acheter(self, symbole, quantite, date=None):
        """Méthode achats"""
        date = date or datetime.now().date()
        self.valider_date(date)

        prix_achat = self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) * quantite

        if prix_achat > self.liquidites:
            raise LiquiditéInsuffisante("Liquidités insuffisantes pour effectuer l'achat.")

        self.actions[symbole] = self.actions.get(symbole, 0) + quantite
        self.liquidites -= prix_achat
        self.enregistrer_transaction('Achat', prix_achat, date)

    def vendre(self, symbole, quantite, date=None):
        """Méthode vente"""
        date = date or datetime.now().date()
        self.valider_date(date)

        if symbole not in self.actions or self.actions[symbole] < quantite:
            raise ErreurQuantité("Quantité insuffisante d'actions à vendre.")

        prix_vente = self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) * quantite
        self.actions[symbole] -= quantite
        self.liquidites += prix_vente
        self.enregistrer_transaction('Vente', prix_vente, date)

    def valeur_totale(self, date=None):
        """Méthode pour indiquer valeur totale"""
        date = date or datetime.now().date()
        self.valider_date(date)

        valeur_liquidites = self.liquidites
        valeur_titres = sum(self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) * quantite
                            for symbole, quantite in self.actions.items())
        return valeur_liquidites + valeur_titres

    def valeur_des_titres(self, symboles, date=None):
        """Méthode pour indiquer la valeur des titres"""
        date = date or datetime.now().date()
        self.valider_date(date)

        return sum(self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) * quantite
                   for symbole, quantite in self.actions.items() if symbole in symboles)

    def lister(self, date=None):
        """Autre méthode"""
        date = date or datetime.now().date()
        self.valider_date(date)

        self.charger_portfolio()

        for symbole, quantite in self.titres(date).items():
            prix_unitaire = self.bourse.prix(symbole, date.strftime('%Y-%m-%d'))
            montant = quantite * prix_unitaire
            print(f"{symbole} = {quantite} x {prix_unitaire} = {montant}")

        self.sauvegarder_portfolio()

    def titres(self, date=None):
        """Autre méthode"""
        date = date or datetime.now().date()
        self.valider_date(date)

        return dict(self.actions.items())

    def valeur_projetee(self, date, rendement):
        """Définition de la méthode valeur_projetee"""
        if date <= datetime.now().date():
            raise ErreurDate("La date future spécifiée est antérieure ou égale à la date du jour.")

        valeur_projetee = self.liquidites + sum(
            quantite * self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) *
            (1 + rendement.get(symbole, 0) / 100)for symbole, quantite in self.actions.items())
        return valeur_projetee

class PortefeuilleGraphique(Portefeuille):
    """Classe pour créer un graphe"""
    def graphique_historique(self, symboles, date_fin=None):
        """Méthode pour vérifier historique"""
        date_fin = date_fin or datetime.now().date()
        self.valider_date(date_fin)

        dates = [date_fin - timedelta(days=x) for x in range(365)]
        valeurs_titres = {symbole: [] for symbole in symboles}

        for date in reversed(dates):
            for symbole in symboles:
                prix_unitaire = self.bourse.prix(symbole, date.strftime('%Y-%m-%d'))
                quantite = self.actions.get(symbole, 0)
                montant = quantite * prix_unitaire
                valeurs_titres[symbole].append(montant)

        plt.figure(figsize=(10, 6))
        for symbole, valeurs in valeurs_titres.items():
            plt.plot(dates, valeurs, label=symbole)

        plt.title('Historique des valeurs des actions')
        plt.xlabel('Date')
        plt.ylabel('Valeur de l\'action')
        plt.legend()
        plt.show()

    def graphique_projection(self,
                             symboles,
                             date_debut=None,
                             date_fin=None,
                             rendement=None,
                             volatilite=None,
                             nombre_projections=1000):
        """Méthode projection"""
        date_debut = date_debut or datetime.now().date()
        date_fin = date_fin or (datetime.now().date() + timedelta(days=365))
        self.valider_date(date_debut)
        self.valider_date(date_fin)

        dates = [date_debut + timedelta(days=x) for x in range((date_fin - date_debut).days + 1)]

        projections = []

        for _ in range(nombre_projections):
            valeurs_titres = []
            for symbole in symboles:
                rendement_symbole = rendement.get(symbole, 0) + np.random.normal(
                    0, volatilite.get(symbole, 0) / 100
                    )
                projections_symbole = [self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) *
                                       (1 + rendement_symbole)
                                        for date in dates]
                valeurs_titres.extend(projections_symbole)

            projections.append(valeurs_titres)

        projections = np.array(projections)
        quartiles = np.percentile(projections, [25, 50, 75], axis=0)

        plt.figure(figsize=(10, 6))
        plt.plot(dates, quartiles[1], label='Médiane')
        plt.fill_between(dates, quartiles[0], quartiles[2], alpha=0.2, label='Écart interquartile')

        plt.title('Projection des valeurs des actions')
        plt.xlabel('Date')
        plt.ylabel('Valeur projetée')
        plt.legend()
        plt.show()
