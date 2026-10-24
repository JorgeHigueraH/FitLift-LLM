def calcular_e1rm_epley(peso: float, repeticiones: int) -> float:
    """Estimación Epley. No es una medición directa del 1RM."""
    peso = float(peso)
    repeticiones = int(repeticiones)
    if peso <= 0:
        raise ValueError("El peso debe ser mayor que cero.")
    if repeticiones < 1:
        raise ValueError("Las repeticiones deben ser al menos 1.")
    return peso * (1 + repeticiones / 30.0)
