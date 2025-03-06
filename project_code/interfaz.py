import customtkinter as ctk
import tkinter as tk
from optimizacion import resolver_optimizacion
from grafica import dibujar_grafico

class FilaDeRestricciones(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.entry_a = ctk.CTkEntry(self, width=50, placeholder_text="a")
        self.entry_a.grid(row=0, column=0, padx=5, pady=5)
        self.entry_b = ctk.CTkEntry(self, width=50, placeholder_text="b")
        self.entry_b.grid(row=0, column=1, padx=5, pady=5)
        self.entry_c = ctk.CTkEntry(self, width=50, placeholder_text="c")
        self.entry_c.grid(row=0, column=2, padx=5, pady=5)
        self.var_ineq = ctk.StringVar(value="<=")
        self.dropdown = ctk.CTkOptionMenu(self, values=["<=", ">="], variable=self.var_ineq)
        self.dropdown.grid(row=0, column=3, padx=5, pady=5)
        
    def obtener_restriccion(self):
        try:
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            c = float(self.entry_c.get())
            ineq = self.var_ineq.get()
            return {'a': a, 'b': b, 'c': c, 'inecuacion': ineq}
        except ValueError:
            return None

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Optimización Lineal - GUI")
        self.geometry("1000x600")
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        
        self.frame_left = ctk.CTkFrame(self, width=300)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.label_obj = ctk.CTkLabel(self.frame_left, text="Función Objetivo (Z = ax + by)")
        self.label_obj.pack(pady=5)
        
        self.frame_obj = ctk.CTkFrame(self.frame_left)
        self.frame_obj.pack(pady=5)
        
        self.entry_obj_a = ctk.CTkEntry(self.frame_obj, width=50, placeholder_text="a")
        self.entry_obj_a.grid(row=0, column=0, padx=5, pady=5)
        self.entry_obj_b = ctk.CTkEntry(self.frame_obj, width=50, placeholder_text="b")
        self.entry_obj_b.grid(row=0, column=1, padx=5, pady=5)
        
        self.var_obj_type = ctk.StringVar(value="max")
        self.dropdown_obj_type = ctk.CTkOptionMenu(self.frame_obj, values=["max", "min"], variable=self.var_obj_type)
        self.dropdown_obj_type.grid(row=0, column=2, padx=5, pady=5)
        
        self.label_constraints = ctk.CTkLabel(self.frame_left, text="Restricciones (inecuaciones)")
        self.label_constraints.pack(pady=5)
        
        self.frame_constraints = ctk.CTkFrame(self.frame_left)
        self.frame_constraints.pack(pady=5)
        
        self.filas_restricciones = []
        self.añadir_fila_restriccion(default={'a': 1, 'b': 0, 'c': 0, 'inecuacion': '>='})
        self.añadir_fila_restriccion(default={'a': 0, 'b': 1, 'c': 0, 'inecuacion': '>='})
        
        self.button_add = ctk.CTkButton(self.frame_left, text="+ Añadir Restricción", command=self.añadir_fila_restriccion)
        self.button_add.pack(pady=5)
        
        self.button_remove = ctk.CTkButton(self.frame_left, text="- Eliminar Última Restricción", command=self.remover_fila_restriccion)
        self.button_remove.pack(pady=5)
        
        self.button_solve = ctk.CTkButton(self.frame_left, text="Resolver Optimización", command=self.resolver)
        self.button_solve.pack(pady=10)
        
        self.text_output = ctk.CTkTextbox(self.frame_left, height=150)
        self.text_output.pack(pady=5, fill="both", expand=True)
        
    def añadir_fila_restriccion(self, default=None):
        fila = FilaDeRestricciones(self.frame_constraints)
        fila.pack(pady=2, fill="x")
        if default:
            fila.entry_a.insert(0, str(default['a']))
            fila.entry_b.insert(0, str(default['b']))
            fila.entry_c.insert(0, str(default['c']))
            fila.var_ineq.set(default['inecuacion'])
        self.filas_restricciones.append(fila)
        
    def remover_fila_restriccion(self):
        if self.filas_restricciones:
            filas = self.filas_restricciones.pop()
            filas.destroy()
        
    def resolver(self):
        self.text_output.delete("1.0", tk.END)
        
        try:
            a_obj = float(self.entry_obj_a.get())
            b_obj = float(self.entry_obj_b.get())
        except ValueError:
            self.text_output.insert(tk.END, "Error en los coeficientes de la función objetivo.\n")
            return
        objetivo = {'coeff': [a_obj, b_obj], 'type': self.var_obj_type.get()}
        
        restricciones = []
        for fila in self.filas_restricciones:
            restriccion = fila.obtener_restriccion()
            if restriccion is None:
                self.text_output.insert(tk.END, "Error en los datos de alguna restricción.\n")
                return
            restricciones.append(restriccion)
        
        resultado, mensaje, puntos_factibles = resolver_optimizacion(objetivo, restricciones)
        self.text_output.insert(tk.END, mensaje + "\n")
        
        if resultado is None:
            return
        
        dibujar_grafico(restricciones, puntos_factibles, resultado['punto_optimo'], self.frame_right)
