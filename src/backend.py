import random

class RFIDBackend:
    def __init__(self):
        self.tracked_objects = ["Cartera", "Llaves", "Mochila"]

    def check_objects(self):
        """Simula la detección de objetos fuera de rango"""
        if random.random() < 0.3:  # Simulación de 30% de probabilidad de pérdida
            return random.choice(self.tracked_objects)
        return None
