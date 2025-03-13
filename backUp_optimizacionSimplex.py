import numpy as np
from itertools import combinations

def encontrar_interseccion(restricciones):
    """
    Encuentra la intersección de n restricciones (sistema de ecuaciones lineales).
    """
    A = np.array([[r['a'][i] for i in range(len(restricciones[0]['a']))] for r in restricciones])
    b = np.array([r['c'] for r in restricciones])
    
    try:
        x = np.linalg.solve(A, b)
        return tuple(x)
    except np.linalg.LinAlgError:
        return None  # No hay solución única (sistema singular o incompatible)

def es_factible(punto, restricciones):
    """
    Verifica si un punto satisface todas las restricciones.
    """
    for r in restricciones:
        lhs = sum(r['a'][i] * punto[i] for i in range(len(punto)))
        if r['inecuacion'] == '<=' and lhs > r['c'] + 1e-9:
            return False
        elif r['inecuacion'] == '>=' and lhs < r['c'] - 1e-9:
            return False
    return True

def resolver_optimizacion(objetivo, restricciones):
    """
    Resuelve un problema de optimización lineal con n variables.
    """
    n_variables = len(restricciones[0]['a'])  # Número de variables de decisión
    intersecciones = []
    
    # Generar todas las combinaciones de n_variables restricciones
    for restricciones_combinadas in combinations(restricciones, n_variables):
        punto = encontrar_interseccion(restricciones_combinadas)
        if punto is not None:
            intersecciones.append(punto)
    
    # Filtrar puntos factibles
    puntos_factibles = [punto for punto in intersecciones if es_factible(punto, restricciones)]
    puntos_factibles = list(set([tuple(round(coord, 3) for coord in punto) for punto in puntos_factibles]))
    
    if not puntos_factibles:
        return None, "No hay solución factible", []
    
    # Evaluar la función objetivo en los puntos factibles
    coeficiente_objetivo = objetivo['coeff']
    tipo_objetivo = objetivo['type']
    valores = []
    for punto in puntos_factibles:
        z = sum(coeficiente_objetivo[i] * punto[i] for i in range(n_variables))
        valores.append((z, punto))
    
    # Encontrar el óptimo
    if tipo_objetivo == 'max':
        optimo = max(valores, key=lambda v: v[0])
    else:
        optimo = min(valores, key=lambda v: v[0])
    
    # Mensaje de salida
    mensaje = (f"Solución óptima en {optimo[1]}\n"
               f"Valor óptimo: {optimo[0]:.2f}")
    return {'punto_optimo': optimo[1], 'valor_optimo': optimo[0]}, mensaje, puntos_factibles