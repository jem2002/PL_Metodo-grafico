import numpy as np

def encontrar_interseccion(restriccion1, restriccion2):
    a1, b1, c1 = restriccion1['a'], restriccion1['b'], restriccion1['c']
    a2, b2, c2 = restriccion2['a'], restriccion2['b'], restriccion2['c']
    
    denominador = a1 * b2 - a2 * b1
    if abs(denominador) < 1e-9:
        return None
    x = (b2 * c1 - b1 * c2) / denominador
    y = (a1 * c2 - a2 * c1) / denominador
    return (x, y)

def es_factible(x, y, restricciones):
    for r in restricciones:
        lhs = r['a'] * x + r['b'] * y
        if r['inecuacion'] == '<=' and lhs > r['c'] + 1e-9:
            return False
        elif r['inecuacion'] == '>=' and lhs < r['c'] - 1e-9:
            return False
    return True

def resolver_optimizacion(objetivo, restricciones):
    intersecciones = []
    n = len(restricciones)
    for i in range(n):
        for j in range(i+1, n):
            punto = encontrar_interseccion(restricciones[i], restricciones[j])
            if punto is not None:
                intersecciones.append(punto)
    
    puntos_factibles = []
    for punto in intersecciones:
        x, y = punto
        if es_factible(x, y, restricciones):
            puntos_factibles.append((x, y))
    
    puntos_factibles = list(set([(round(x, 3), round(y, 3)) for (x, y) in puntos_factibles]))
    
    if not puntos_factibles:
        return None, "No hay solución factible", []
    
    coeficiente_objetivo = objetivo['coeff']
    tipo_objetivo = objetivo['type']
    valores = []
    for punto in puntos_factibles:
        x, y = punto
        z = coeficiente_objetivo[0] * x + coeficiente_objetivo[1] * y
        valores.append((z, punto))
    
    if tipo_objetivo == 'max':
        optimo = max(valores, key=lambda v: v[0])
    else:
        optimo = min(valores, key=lambda v: v[0])
    
    mensaje = (f"Solución óptima en (x, y) = ({optimo[1][0]:.2f}, {optimo[1][1]:.2f})\n"
            f"Valor óptimo: {optimo[0]:.2f}")
    return {'punto_optimo': optimo[1], 'valor_optimo': optimo[0]}, mensaje, puntos_factibles
