"""Module permettant de lever des exceptions"""
class ErreurDate(RuntimeError):
    """Classe pour encapsuler les erreurs de date"""
    def __init__(self, message="Erreur de date"):
        """Exception levée pour des erreurs liées à des dates."""
        self.message = message
        super().__init__(self.message)

class ErreurQuantité(RuntimeError):
    """Classe pour encapsuler les erreurs de quantié"""
    def __init__(self, message="Erreur de quantité"):
        """Exception levée pour des erreurs liées à la quantité"""
        self.message = message
        super().__init__(self.message)

class LiquiditéInsuffisante(RuntimeError):
    """Classe pour encapsuler les erreurs liées à la liquidité"""
    def __init__(self, message="Liquidité insuffisante"):
        """Exception levée pour des erreurs liées à la liquidité."""
        self.message = message
        super().__init__(self.message)