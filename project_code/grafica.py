import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def is_feasible(x, y, restricciones):
    for r in restricciones:
        lhs = r['a'] * x + r['b'] * y
        if r['inequality'] == '<=' and lhs > r['c'] + 1e-9:
            return False
        elif r['inequality'] == '>=' and lhs < r['c'] - 1e-9:
            return False
    return True

def plot_graph(objective, restricciones, feasible_points, optimal_point, container):
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    
    x_max = max([p[0] for p in feasible_points]) + 2 if feasible_points else 10
    y_max = max([p[1] for p in feasible_points]) + 2 if feasible_points else 10
    
    for r in restricciones:
        a, b, c = r['a'], r['b'], r['c']
        ineq = r['inequality']
        x_vals = np.linspace(0, x_max, 400)
        if b != 0:
            y_vals = (c - a * x_vals) / b
            ax.plot(x_vals, y_vals, label=f'{a}x + {b}y {ineq} {c}')
            if is_feasible(0, 0, [r]):
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
    
    if len(feasible_points) >= 3:
        centroid = (np.mean([p[0] for p in feasible_points]), np.mean([p[1] for p in feasible_points]))
        sorted_points = sorted(feasible_points, key=lambda p: np.arctan2(p[1]-centroid[1], p[0]-centroid[0]))
        polygon = np.array(sorted_points)
        ax.fill(polygon[:,0], polygon[:,1], color='gray', alpha=0.3, label='Región Factible')
    
    if feasible_points:
        ax.scatter(*zip(*feasible_points), color='red', zorder=5)
    ax.scatter(optimal_point[0], optimal_point[1], color='green', marker='*', s=200, label='Solución Óptima')
    
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
