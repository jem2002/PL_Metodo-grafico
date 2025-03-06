import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def es_factible(x, y, restricciones):
    for r in restricciones:
        lhs = r['a'] * x + r['b'] * y
        if r['inecuacion'] == '<=' and lhs > r['c'] + 1e-9:
            return False
        elif r['inecuacion'] == '>=' and lhs < r['c'] - 1e-9:
            return False
    return True

def dibujar_grafico(restricciones, puntos_factibles, punto_optimo, container):
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    
    x_max = max([p[0] for p in puntos_factibles]) + 2 if puntos_factibles else 10
    y_max = max([p[1] for p in puntos_factibles]) + 2 if puntos_factibles else 10
    
    for r in restricciones:
        a, b, c = r['a'], r['b'], r['c']
        ineq = r['inecuacion']
        x_vals = np.linspace(0, x_max, 400)
        if b != 0:
            y_vals = (c - a * x_vals) / b
            ax.plot(x_vals, y_vals, label=f'{a}x + {b}y {ineq} {c}')
            if es_factible(0, 0, [r]):
                ax.fill_between(x_vals, y_vals, -10, alpha=0.1)
            else:
                ax.fill_between(x_vals, y_vals, 10, alpha=0.1)
        else:
            x_line = c / a
            ax.axvline(x=x_line, label=f'x {ineq} {c/a:.2f}')
            if ineq == '<=':
                ax.fill_betweenx(y=np.linspace(0, y_max, 400), x1=x_line, x2=-10, alpha=0.1)
            else:
                ax.fill_betweenx(y=np.linspace(0, y_max, 400), x1=x_line, x2=10, alpha=0.1)
    
    if len(puntos_factibles) >= 3:
        centroid = (np.mean([p[0] for p in puntos_factibles]), np.mean([p[1] for p in puntos_factibles]))
        sorted_points = sorted(puntos_factibles, key=lambda p: np.arctan2(p[1]-centroid[1], p[0]-centroid[0]))
        polygon = np.array(sorted_points)
        ax.fill(polygon[:,0], polygon[:,1], color='gray', alpha=0.3, label='Región Factible')
    
    if puntos_factibles:
        ax.scatter(*zip(*puntos_factibles), color='red', zorder=5)
    ax.scatter(punto_optimo[0], punto_optimo[1], color='green', marker='*', s=200, label='Solución Óptima')
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Método Gráfico para Programación Lineal')
    ax.legend()
    ax.grid(True)
    
    for widget in container.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
