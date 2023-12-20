from datetime import datetime
from exceptions import ErreurDate, ErreurQuantité, LiquiditéInsuffisante
from bourse import Bourse
import json

class Portefeuille:
    """Création de la classe portefeuille"""
    def _init_(self, bourse, nom_portefeuille=None):
        self.bourse = bourse
        self.nom_portefeuille = nom_portefeuille
        self.liquidites = 0
        self.actions = {}
        self.transactions = []
        self.charger_portfolio()

    def charger_portfolio(self):
        """Méthode charger_portfolio"""
        try:
            with open(f'{self.nom_portefeuille}.json', 'r') as file:
                data = json.load(file)
                self.liquidites = data.get('liquidites', 0)
                self.actions = data.get('actions', {})
        except FileNotFoundError:
            self.liquidites = 0
            self.actions = {}

    def sauvegarder_portfolio(self):
        data = {'liquidites': self.liquidites, 'actions': self.actions}
        with open(f'{self.nom_portefeuille}.json', 'w') as file:
            json.dump(data, file)

    def valider_date(self, date):
        if date > datetime.now().date():
            raise ErreurDate("La date spécifiée est postérieure à la date du jour.")
    
    def enregistrer_transaction(self, type_transaction, montant, date):
        self.transactions.append({'type': type_transaction, 'montant': montant, 'date': date})

    def deposer(self, montant, date=None):
        date = date or datetime.now().date()
        self.valider_date(date)
        self.liquidites += montant
        self.enregistrer_transaction('Dépôt', montant, date)

    def solde(self, date=None):
        date = date or datetime.now().date()
        self.valider_date(date)
        return self.liquidites

    def acheter(self, symbole, quantite, date=None):
        date = date or datetime.now().date()
        self.valider_date(date)

        prix_achat = self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) * quantite

        if prix_achat > self.liquidites:
            raise LiquiditéInsuffisante("Liquidités insuffisantes pour effectuer l'achat.")

        self.actions[symbole] = self.actions.get(symbole, 0) + quantite
        self.liquidites -= prix_achat
        self.enregistrer_transaction('Achat', prix_achat, date)

    def vendre(self, symbole, quantite, date=None):
        date = date or datetime.now().date()
        self.valider_date(date)

        if symbole not in self.actions or self.actions[symbole] < quantite:
            raise ErreurQuantité("Quantité insuffisante d'actions à vendre.")

        prix_vente = self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) * quantite
        self.actions[symbole] -= quantite
        self.liquidites += prix_vente
        self.enregistrer_transaction('Vente', prix_vente, date)

    def valeur_totale(self, date=None):
        date = date or datetime.now().date()
        self.valider_date(date)

        valeur_liquidites = self.liquidites
        valeur_titres = sum(self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) * quantite
                            for symbole, quantite in self.actions.items())
        return valeur_liquidites + valeur_titres

    def valeur_des_titres(self, symboles, date=None):
        date = date or datetime.now().date()
        self.valider_date(date)

        return sum(self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) * quantite
                   for symbole, quantite in self.actions.items() if symbole in symboles)

    def lister(self, date=None):
        date = date or datetime.now().date()
        self.valider_date(date)

        self.charger_portfolio()

        for symbole, quantite in self.titres(date).items():
            prix_unitaire = self.bourse.prix(symbole, date.strftime('%Y-%m-%d'))
            montant = quantite * prix_unitaire
            print(f"{symbole} = {quantite} x {prix_unitaire} = {montant}")

        self.sauvegarder_portfolio()

    def titres(self, date=None):
        date = date or datetime.now().date()
        self.valider_date(date)

        return {symbole: quantite for symbole, quantite in self.actions.items()}

    def valeur_projetee(self, date, rendement):
        """Définition de la méthode valeur_projetee"""
        if date <= datetime.now().date():
            raise ErreurDate("La date future spécifiée est antérieure ou égale à la date du jour.")

        valeur_projetee = self.liquidites + sum(quantite * self.bourse.prix(symbole, date.strftime('%Y-%m-%d')) *(1 + rendement.get(symbole, 0) / 100)for symbole, quantite in self.actions.items())
        
        return valeur_projetee

    

