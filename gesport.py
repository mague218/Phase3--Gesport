import argparse
from datetime import datetime
from bourse import Bourse
from portefeuille import Portefeuille
from exceptions import *

def analyser_commande():
    parser = argparse.ArgumentParser(description="Système de gestion de portefeuille financier")
    parser.add_argument('action',
                        choices=['deposer', 'acheter', 'vendre', 'lister', 'projeter'],
                        help='Action à effectuer')
    parser.add_argument('-d',
                        '--date',
                        help='Date effective (par défaut, la date du jour)')
    parser.add_argument('-q',
                        '--quantite',
                        type=int,
                        default=1,
                        help='Quantité désirée (par défaut : 1)')
    parser.add_argument('-t',
                        '--titres',
                        nargs='+',
                        help='Le ou les titres à considérer')
    parser.add_argument('-r',
                        '--rendement',
                        type=float,
                        default=0,
                        help='Rendement annuel global (par défaut : 0)')
    parser.add_argument('-v',
                        '--volatilite',
                        type=float,
                        default=0,
                        help='Indice de volatilité global sur le rendement annuel (par défaut : 0)')
    parser.add_argument('-g',
                        '--graphique',
                        action='store_true',
                        help='Affichage graphique (par défaut, pas d\'affichage graphique)')
    parser.add_argument('-p',
                        '--portefeuille',
                        default='folio',
                        help='Nom du portefeuille (par défaut, folio)')
    return parser.parse_args()

def principal():
    commande = analyser_commande()
    bourses = Bourse()
    portefeuille = Portefeuille(bourses, commande.portefeuille)
    
    if commande.date is None:
        date_obj = datetime.now().date()
    else:
        datetime.strptime(commande.date, '%Y-%m-%d').date()
    # Exécuter la méthode correspondante en fonction de l'action
    if commande.action == 'deposer':
        portefeuille.charger_portfolio()
        portefeuille.deposer(int(commande.quantite), date_obj)
    elif commande.action == 'acheter':
        portefeuille.charger_portfolio()
        portefeuille.acheter(commande.titres[0], commande.quantite, date_obj)
    elif commande.action == 'vendre':
        portefeuille.charger_portfolio()
        portefeuille.vendre(commande.titres[0], commande.quantite, date_obj)
    elif commande.action == 'lister':
        portefeuille.lister(datetime.now().date())
        if commande.graphique:
            portefeuille.graphique_listing(date_obj)
    elif commande.action == 'projeter':
        valeur_projetee = portefeuille.valeur_projetee(date_obj, commande.rendement)
        print(f"Valeur projetée = {valeur_projetee}")
    
    # Afficher le solde actuel et sauvegarder le portefeuille
    print(f"Solde = {portefeuille.solde(date_obj)}")
    portefeuille.sauvegarder_portfolio()

if __name__ == '__main__':
    principal()
