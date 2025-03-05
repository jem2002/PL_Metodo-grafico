import numpy as np
import matplotlib.pyplot as plt

def graficar(restricciones, puntos_factibles, objetivo, optimo):

    plt.figure(figsize=(10, 6))
    
    # Graficar restricciones
    for restriccion in restricciones:
        a, b, c = restriccion['a'], restriccion['b'], restriccion['c']
        ineq = restriccion['inecuacion']
        
        x_vals = np.linspace(0, max(p[0] for p in puntos_factibles) + 2, 400)
        
        if b != 0:
            y_vals = (c - a * x_vals) / b
            plt.plot(x_vals, y_vals, label=f'{a}x + {b}y {ineq} {c}')
            # Sombrear región factible
            if es_factible(0, 0, [restriccion]):
                plt.fill_between(x_vals, y_vals, -10, alpha=0.1)
            else:
                plt.fill_between(x_vals, y_vals, 10, alpha=0.1)
        else:
            x_line = c / a
            plt.axvline(x=x_line, label=f'x {ineq} {c/a:.2f}')
            if ineq == '<=':
                plt.fill_betweenx(y=np.linspace(0, max(p[1] for p in puntos_factibles) + 2, 400),
                                x1=x_line, x2=-10, alpha=0.1)
            else:
                plt.fill_betweenx(y=np.linspace(0, max(p[1] for p in puntos_factibles) + 2, 400),
                                x1=x_line, x2=10, alpha=0.1)
    
    # Graficar región factible
    if len(puntos_factibles) >= 3:
        puntos_ordenados = sorted(puntos_factibles,
                                key=lambda p: np.arctan2(p[1]-np.mean([p[1] for p in puntos_factibles]),
                                                    p[0]-np.mean([p[0] for p in puntos_factibles])))
        plt.fill(*zip(*puntos_ordenados), 'gray', alpha=0.3, label='Región Factible')
    
    plt.scatter(*zip(*puntos_factibles), color='red', zorder=5)
    plt.scatter(optimo[1][0], optimo[1][1], color='green', marker='*', s=200, label='Solución Óptima')
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Método Gráfico para Programación Lineal')
    plt.legend()
    plt.grid(True)
    plt.show()

def es_factible(x, y, restricciones):
    for r in restricciones:
        lhs = r['a'] * x + r['b'] * y
        if r['inecuacion'] == '<=' and lhs > r['c'] + 1e-9:
            return False
        elif r['inecuacion'] == '>=' and lhs < r['c'] - 1e-9:
            return False
    return True