import numpy as np
from itertools import combinations

def encontrar_interseccion(restricciones):
    """
    Encuentra la intersección de n restricciones (sistema de ecuaciones lineales).
    """
    if not restricciones:
        return None
    
    n_variables = len(restricciones[0]['a'])
    A = np.array([r['a'] for r in restricciones])
    b = np.array([r['c'] for r in restricciones])
    
    try:
        x = np.linalg.solve(A, b)
        return tuple(x)
    except np.linalg.LinAlgError:
        return None  # No hay solución única o sistema incompatible

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

def inicializar_tabla_simplex(objetivo, restricciones):
    """
    Inicializa la tabla simplex a partir de la función objetivo y las restricciones.
    """
    n_variables = len(objetivo['coeff'])
    n_restricciones = len(restricciones)
    
    # Coeficientes de la función objetivo (multiplicados por -1 para maximizar)
    c = np.array([-coeff for coeff in objetivo['coeff']])
    
    # Matriz de coeficientes de las restricciones
    A = np.array([r['a'] for r in restricciones])
    b = np.array([r['c'] for r in restricciones])
    
    # Identidad para las variables de holgura
    identidad = np.eye(n_restricciones)
    
    # Tabla simplex inicial
    tabla = np.hstack((A, identidad, b.reshape(-1, 1)))
    tabla = np.vstack((tabla, np.hstack((c, np.zeros(n_restricciones + 1)))))
    
    return tabla

def encontrar_columna_pivote(tabla):
    """
    Encuentra la columna pivote (la más negativa en la última fila).
    """
    return np.argmin(tabla[-1, :-1])

def encontrar_fila_pivote(tabla, col_pivote):
    """
    Encuentra la fila pivote usando la regla del mínimo cociente.
    """
    ratios = []
    for i in range(len(tabla) - 1):
        if tabla[i, col_pivote] > 0:
            ratios.append(tabla[i, -1] / tabla[i, col_pivote])
        else:
            ratios.append(np.inf)
    return np.argmin(ratios)

def actualizar_tabla(tabla, fila_pivote, col_pivote):
    """
    Actualiza la tabla simplex usando la operación de pivote.
    """
    tabla[fila_pivote] /= tabla[fila_pivote, col_pivote]
    for i in range(len(tabla)):
        if i != fila_pivote:
            tabla[i] -= tabla[i, col_pivote] * tabla[fila_pivote]

def es_optimo(tabla):
    """
    Verifica si la solución actual es óptima.
    """
    return all(tabla[-1, :-1] >= 0)

def resolver_simplex(objetivo, restricciones):
    """
    Resuelve el problema usando el método simplex.
    """
    tabla = inicializar_tabla_simplex(objetivo, restricciones)
    
    while not es_optimo(tabla):
        col_pivote = encontrar_columna_pivote(tabla)
        fila_pivote = encontrar_fila_pivote(tabla, col_pivote)
        actualizar_tabla(tabla, fila_pivote, col_pivote)
    
    # Extraer solución óptima
    n_variables = len(objetivo['coeff'])
    solucion = np.zeros(n_variables)
    
    for i in range(n_variables):
        col = tabla[:, i]
        if np.sum(col == 1) == 1 and np.sum(col == 0) == len(col) - 1:
            fila = np.where(col == 1)[0][0]
            solucion[i] = tabla[fila, -1]
    
    valor_optimo = tabla[-1, -1]
    
    return solucion, valor_optimo

def resolver_optimizacion(objetivo, restricciones):
    """
    Resuelve el problema y devuelve la solución óptima, valor óptimo y puntos factibles.
    """
    try:
        # Resolver usando simplex
        solucion, valor_optimo = resolver_simplex(objetivo, restricciones)
        
        # Calcular puntos factibles (intersecciones de restricciones)
        n_variables = len(objetivo['coeff'])
        intersecciones = []
        
        # Generar combinaciones de n_variables restricciones
        for restricciones_combinadas in combinations(restricciones, n_variables):
            punto = encontrar_interseccion(restricciones_combinadas)
            if punto is not None:
                intersecciones.append(punto)
        
        # Filtrar puntos factibles
        puntos_factibles = [p for p in intersecciones if es_factible(p, restricciones)]
        puntos_factibles = list(set([tuple(round(coord, 3) for coord in p) for p in puntos_factibles]))
        
        # Mensaje de salida
        mensaje = (f"Solución óptima: {solucion}\n"
                   f"Valor óptimo: {valor_optimo:.2f}")
        
        return {'punto_optimo': solucion, 'valor_optimo': valor_optimo}, mensaje, puntos_factibles
    
    except Exception as e:
        return None, f"Error: {str(e)}", []