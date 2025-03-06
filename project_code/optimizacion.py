import numpy as np

def find_intersection(restriccion1, restriccion2):
    a1, b1, c1 = restriccion1['a'], restriccion1['b'], restriccion1['c']
    a2, b2, c2 = restriccion2['a'], restriccion2['b'], restriccion2['c']
    
    denominador = a1 * b2 - a2 * b1
    if abs(denominador) < 1e-9:
        return None
    x = (b2 * c1 - b1 * c2) / denominador
    y = (a1 * c2 - a2 * c1) / denominador
    return (x, y)

def is_feasible(x, y, restricciones):
    for r in restricciones:
        lhs = r['a'] * x + r['b'] * y
        if r['inequality'] == '<=' and lhs > r['c'] + 1e-9:
            return False
        elif r['inequality'] == '>=' and lhs < r['c'] - 1e-9:
            return False
    return True

def solve_optimization(objective, restricciones):
    intersections = []
    n = len(restricciones)
    for i in range(n):
        for j in range(i+1, n):
            point = find_intersection(restricciones[i], restricciones[j])
            if point is not None:
                intersections.append(point)
    
    feasible_points = []
    for point in intersections:
        x, y = point
        if is_feasible(x, y, restricciones):
            feasible_points.append((x, y))
    
    feasible_points = list(set([(round(x, 3), round(y, 3)) for (x, y) in feasible_points]))
    
    if not feasible_points:
        return None, "No hay solución factible", []
    
    obj_coeff = objective['coeff']
    obj_type = objective['type']
    valores = []
    for punto in feasible_points:
        x, y = punto
        z = obj_coeff[0] * x + obj_coeff[1] * y
        valores.append((z, punto))
    
    if obj_type == 'max':
        optimo = max(valores, key=lambda v: v[0])
    else:
        optimo = min(valores, key=lambda v: v[0])
    
    mensaje = (f"Solución óptima en (x, y) = ({optimo[1][0]:.2f}, {optimo[1][1]:.2f})\n"
            f"Valor óptimo: {optimo[0]:.2f}")
    return {'optimal_point': optimo[1], 'optimal_value': optimo[0]}, mensaje, feasible_points
