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
        return tuple(float(round(val, 2)) for val in x)  # Redondear a 2 decimales
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
    if objetivo['type'] == 'max':
        c = np.array([-coeff for coeff in objetivo['coeff']])
    else:  # minimización
        c = np.array(objetivo['coeff'])
    
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
    Devuelve la solución óptima, el valor óptimo y las tablas intermedias.
    """
    tabla = inicializar_tabla_simplex(objetivo, restricciones)
    tablas_intermedias = [tabla.copy()]  # Guardar la tabla inicial
    
    while not es_optimo(tabla):
        col_pivote = encontrar_columna_pivote(tabla)
        fila_pivote = encontrar_fila_pivote(tabla, col_pivote)
        actualizar_tabla(tabla, fila_pivote, col_pivote)
        tablas_intermedias.append(tabla.copy())  # Guardar la tabla actualizada
    
    # Extraer solución óptima
    n_variables = len(objetivo['coeff'])
    solucion = np.zeros(n_variables)
    
    for i in range(n_variables):
        col = tabla[:, i]
        if np.sum(col == 1) == 1 and np.sum(col == 0) == len(col) - 1:
            fila = np.where(col == 1)[0][0]
            solucion[i] = tabla[fila, -1]
    
    valor_optimo = tabla[-1, -1]
    
    # Convertir y redondear la solución a tipos nativos de Python
    solucion = [float(round(x, 2)) for x in solucion]  # Redondear a 2 decimales
    valor_optimo = float(round(valor_optimo, 2))  # Redondear a 2 decimales
    
    return solucion, valor_optimo, tablas_intermedias

def resolver_optimizacion(objetivo, restricciones):
    """
    Resuelve el problema y devuelve la solución óptima, valor óptimo, puntos factibles y tablas intermedias.
    """
    try:
        # Resolver usando simplex
        solucion, valor_optimo, tablas_simplex = resolver_simplex(objetivo, restricciones)
        
        # Verificar si la solución es un vector de ceros
        if all(abs(x) < 1e-9 for x in solucion):
            print("Advertencia: La solución óptima es un vector de ceros. Descartando esta solución.")
            solucion = None
            valor_optimo = None
        
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
        puntos_factibles = list(set([tuple(float(round(coord, 2)) for coord in p) for p in puntos_factibles]))
        
        # Si la solución simplex es un vector de ceros, buscar la mejor solución entre los puntos factibles
        if solucion is None and puntos_factibles:
            mejor_punto = None
            mejor_valor = np.inf if objetivo['type'] == 'min' else -np.inf
            
            for punto in puntos_factibles:
                valor = sum(objetivo['coeff'][i] * punto[i] for i in range(n_variables))
                if (objetivo['type'] == 'min' and valor < mejor_valor) or (objetivo['type'] == 'max' and valor > mejor_valor):
                    mejor_punto = punto
                    mejor_valor = valor
            
            solucion = [float(round(x, 2)) for x in mejor_punto]  # Redondear a 2 decimales
            valor_optimo = float(round(mejor_valor, 2))  # Redondear a 2 decimales
        
        # Mensaje de salida
        if solucion is not None:
            mensaje = (f"Solución óptima: {tuple(solucion)}\n"
                       f"Valor óptimo: {valor_optimo:.2f}")
        else:
            mensaje = "No se encontró una solución óptima válida."
        
        return {'punto_optimo': solucion, 'valor_optimo': valor_optimo}, mensaje, puntos_factibles, tablas_simplex
    
    except Exception as e:
        return None, f"Error: {str(e)}", [], []