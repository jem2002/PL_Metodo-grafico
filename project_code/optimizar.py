import graficar as graf

def resolver_problema_optimizacion(objetivo, restricciones):
    
    # Encontrar intersecciones
    intersecciones = []
    n = len(restricciones)
    for i in range(n):
        for j in range(i+1, n):
            punto = encontrar_interseccion(restricciones[i], restricciones[j])
            if punto is not None:
                intersecciones.append(punto)
    
    # Filtrar puntos factibles
    puntos_factibles = []
    for punto in intersecciones:
        x, y = punto
        if graf.es_factible(x, y, restricciones):
            puntos_factibles.append((x, y))
    
    # Eliminar duplicados
    puntos_factibles = list(set([(round(x, 3), round(y, 3)) for (x, y) in puntos_factibles]))
    
    if not puntos_factibles:
        print("No hay solución factible")
        return
    
    # Evaluar la función objetivo
    obj_coeficiente = objetivo['coeficiente']
    obj_tipo = objetivo['tipo']
    
    valores = []
    for punto in puntos_factibles:
        x, y = punto
        z = obj_coeficiente[0] * x + obj_coeficiente[1] * y
        valores.append((z, punto))
    
    # Encontrar solución óptima
    if obj_tipo == 'max':
        optimo = max(valores, key=lambda v: v[0])
    else:
        optimo = min(valores, key=lambda v: v[0])
    
    print(f"Solución óptima en (x, y) = ({optimo[1][0]:.2f}, {optimo[1][1]:.2f})")
    print(f"Valor óptimo: {optimo[0]:.2f}")

    graf.graficar(restricciones, puntos_factibles, objetivo, optimo)


def encontrar_interseccion(restriccion1, restriccion2):
    a1, b1, c1 = restriccion1['a'], restriccion1['b'], restriccion1['c']
    a2, b2, c2 = restriccion2['a'], restriccion2['b'], restriccion2['c']
    
    denominador = a1 * b2 - a2 * b1
    if denominador == 0:
        return None
    x = (b2 * c1 - b1 * c2) / denominador
    y = (a1 * c2 - a2 * c1) / denominador
    return (x, y)