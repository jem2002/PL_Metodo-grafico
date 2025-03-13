import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D  # Para gráficos 3D

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

def dibujar_grafico(restricciones, puntos_factibles, punto_optimo, container):
    n_variables = len(puntos_factibles[0]) if puntos_factibles else 0
    
    if n_variables == 2:
        _dibujar_grafico_2d(restricciones, puntos_factibles, punto_optimo, container)
    elif n_variables == 3:
        _dibujar_grafico_3d(restricciones, puntos_factibles, punto_optimo, container)
    else:
        print("No se puede graficar para más de 3 variables.")

def _dibujar_grafico_2d(restricciones, puntos_factibles, punto_optimo, container):
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    
    x_max = max([p[0] for p in puntos_factibles]) + 2 if puntos_factibles else 10
    y_max = max([p[1] for p in puntos_factibles]) + 2 if puntos_factibles else 10
    
    for r in restricciones:
        a, b, c = r['a'][0], r['a'][1], r['c']
        ineq = r['inecuacion']
        x_vals = np.linspace(0, x_max, 400)
        
        if a == 0:
            # Caso cuando a = 0 (línea horizontal)
            y_line = c / b
            ax.axhline(y=y_line, label=f'{b}y {ineq} {c}')
            if ineq == '<=':
                ax.fill_between(x_vals, y_line, -10, alpha=0.1)
            else:
                ax.fill_between(x_vals, y_line, 10, alpha=0.1)
        elif b == 0:
            # Caso cuando b = 0 (línea vertical)
            x_line = c / a
            ax.axvline(x=x_line, label=f'x {ineq} {c/a:.2f}')
            if ineq == '<=':
                ax.fill_betweenx(y=np.linspace(0, y_max, 400), x1=x_line, x2=-10, alpha=0.1)
            else:
                ax.fill_betweenx(y=np.linspace(0, y_max, 400), x1=x_line, x2=10, alpha=0.1)
        else:
            # Caso general (línea inclinada)
            y_vals = (c - a * x_vals) / b
            ax.plot(x_vals, y_vals, label=f'{a}x + {b}y {ineq} {c}')
            if es_factible((0, 0), [r]):
                ax.fill_between(x_vals, y_vals, -10, alpha=0.1)
            else:
                ax.fill_between(x_vals, y_vals, 10, alpha=0.1)
    
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
    ax.set_title('Método Gráfico para Programación Lineal (2D)')
    ax.legend()
    ax.grid(True)
    
    for widget in container.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def _dibujar_grafico_3d(restricciones, puntos_factibles, punto_optimo, container):
    fig = plt.figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    
    x_max = max([p[0] for p in puntos_factibles]) + 2 if puntos_factibles else 10
    y_max = max([p[1] for p in puntos_factibles]) + 2 if puntos_factibles else 10
    z_max = max([p[2] for p in puntos_factibles]) + 2 if puntos_factibles else 10
    
    # Graficar restricciones (planos)
    for r in restricciones:
        a, b, c, d = r['a'][0], r['a'][1], r['a'][2], r['c']
        ineq = r['inecuacion']
        
        # Crear malla para el plano
        x_vals, y_vals = np.meshgrid(np.linspace(0, x_max, 10), np.linspace(0, y_max, 10))
        z_vals = (d - a * x_vals - b * y_vals) / c
        
        ax.plot_surface(x_vals, y_vals, z_vals, alpha=0.3, label=f'{a}x + {b}y + {c}z {ineq} {d}')
    
    # Graficar puntos factibles
    if puntos_factibles:
        ax.scatter(*zip(*puntos_factibles), color='red', zorder=5)
    
    # Graficar solución óptima
    ax.scatter(punto_optimo[0], punto_optimo[1], punto_optimo[2], color='green', marker='*', s=200, label='Solución Óptima')
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title('Método Gráfico para Programación Lineal (3D)')
    ax.legend()
    
    for widget in container.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)