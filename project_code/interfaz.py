import customtkinter as ctk
import tkinter as tk
from optimizacion import solve_optimization
from grafica import plot_graph

class ConstraintRow(ctk.CTkFrame):
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
        
    def get_constraint(self):
        try:
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            c = float(self.entry_c.get())
            ineq = self.var_ineq.get()
            return {'a': a, 'b': b, 'c': c, 'inequality': ineq}
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
        self.frame_constraints.pack(pady=5, fill="x")
        
        self.constraint_rows = []
        self.add_constraint_row(default={'a': 1, 'b': 0, 'c': 0, 'inequality': '>='})
        self.add_constraint_row(default={'a': 0, 'b': 1, 'c': 0, 'inequality': '>='})
        
        self.button_add = ctk.CTkButton(self.frame_left, text="+ Añadir Restricción", command=self.add_constraint_row)
        self.button_add.pack(pady=5)
        
        self.button_remove = ctk.CTkButton(self.frame_left, text="- Eliminar Última Restricción", command=self.remove_constraint_row)
        self.button_remove.pack(pady=5)
        
        self.button_solve = ctk.CTkButton(self.frame_left, text="Resolver Optimización", command=self.solve)
        self.button_solve.pack(pady=10)
        
        self.text_output = ctk.CTkTextbox(self.frame_left, height=150)
        self.text_output.pack(pady=5, fill="both", expand=True)
        
    def add_constraint_row(self, default=None):
        row = ConstraintRow(self.frame_constraints)
        row.pack(pady=2, fill="x")
        if default:
            row.entry_a.insert(0, str(default['a']))
            row.entry_b.insert(0, str(default['b']))
            row.entry_c.insert(0, str(default['c']))
            row.var_ineq.set(default['inequality'])
        self.constraint_rows.append(row)
        
    def remove_constraint_row(self):
        if self.constraint_rows:
            row = self.constraint_rows.pop()
            row.destroy()
        
    def solve(self):
        self.text_output.delete("1.0", tk.END)
        
        try:
            a_obj = float(self.entry_obj_a.get())
            b_obj = float(self.entry_obj_b.get())
        except ValueError:
            self.text_output.insert(tk.END, "Error en los coeficientes de la función objetivo.\n")
            return
        objective = {'coeff': [a_obj, b_obj], 'type': self.var_obj_type.get()}
        
        restricciones = []
        for row in self.constraint_rows:
            constraint = row.get_constraint()
            if constraint is None:
                self.text_output.insert(tk.END, "Error en los datos de alguna restricción.\n")
                return
            restricciones.append(constraint)
        
        result, message, feasible_points = solve_optimization(objective, restricciones)
        self.text_output.insert(tk.END, message + "\n")
        
        if result is None:
            return
        
        plot_graph(objective, restricciones, feasible_points, result['optimal_point'], self.frame_right)
