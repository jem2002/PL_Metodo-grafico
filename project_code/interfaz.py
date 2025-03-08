import customtkinter as ctk
import tkinter as tk
import json
import os
import google.generativeai as genai
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

        self.modo_entrada = ctk.StringVar(value="manual")
        self.optionmenu_modo = ctk.CTkOptionMenu(
            self.frame_left, 
            values=["Modo Manual", "Modo Texto"],
            variable=self.modo_entrada,
            command=self.cambiar_modo
        )
        self.optionmenu_modo.pack(pady=10, fill="x")

        self.contenedor_modos = ctk.CTkFrame(self.frame_left)
        self.contenedor_modos.pack(fill="both", expand=True)

        self.frame_manual = ctk.CTkFrame(self.contenedor_modos)
        self.construir_modo_manual()
        
        self.frame_texto = ctk.CTkFrame(self.contenedor_modos)
        self.construir_modo_texto()
        
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.cambiar_modo()

    def construir_modo_manual(self):
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

    def construir_modo_texto(self):
        self.texto_problema = ctk.CTkTextbox(
            self.frame_texto, 
            height=200,
            wrap=tk.WORD
        )
        self.texto_problema.pack(pady=10, fill="both", expand=True)
        
        self.boton_procesar = ctk.CTkButton(
            self.frame_texto,
            text="Procesar Texto",
            command=self.procesar_texto
        )
        self.boton_procesar.pack(pady=5)

    def cambiar_modo(self, *args):
        if "Manual" in self.modo_entrada.get():
            self.frame_texto.pack_forget()
            self.frame_manual.pack(fill="both", expand=True)
        else:
            self.frame_manual.pack_forget()
            self.frame_texto.pack(fill="both", expand=True)

    def procesar_texto(self):
        texto = self.texto_problema.get("1.0", "end-1c")
        if not texto.strip():
            self.text_output.insert(tk.END, "Error: Ingrese un problema de optimización\n")
            return
        
        try:
            resultado = self.llamar_api_ia(texto)
            if not resultado:
                raise ValueError("Error en la respuesta de la API")
            
            self.actualizar_datos_interfaz(resultado)
            self.modo_entrada.set("Modo Manual")
            self.text_output.insert(tk.END, "Datos cargados exitosamente desde el texto\n")
            
        except Exception as e:
            self.text_output.insert(tk.END, f"Error: {str(e)}\n")
    
    def llamar_api_ia(self, texto):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("API key no configurada. Establece GOOGLE_API_KEY en tus variables de entorno")
        
        genai.configure(api_key=api_key)

        prompt = f"""
        Transforma el siguiente problema de programación lineal en formato JSON. 
        Usa exactamente este formato:
        
        {{
            "objetivo": {{
                "coeff": [a, b],
                "type": "max|min"
            }},
            "restricciones": [
                {{
                    "a": número,
                    "b": número,
                    "c": número,
                    "inecuacion": "<="|">="
                }}
            ]
        }}
        
        Considera que:
        - Variables son siempre x e y
        - Inecuaciones pueden estar en cualquier orden
        - Ignora restricciones redundantes
        - Asegúrate de incluir x >= 0 y y >= 0 si son necesarias
        
        Problema:
        {texto}
        """
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            json_str = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(json_str)
            
        except Exception as e:
            raise ValueError(f"Error en Gemini: {str(e)}")
    
    def actualizar_datos_interfaz(self, datos):
        self.entry_obj_a.delete(0, tk.END)
        self.entry_obj_b.delete(0, tk.END)
        while self.filas_restricciones:
            self.remover_fila_restriccion()
        
        objetivo = datos.get("objetivo", {})
        self.entry_obj_a.insert(0, str(objetivo.get("coeff", [0, 0])[0]))
        self.entry_obj_b.insert(0, str(objetivo.get("coeff", [0, 0])[1]))
        self.var_obj_type.set(objetivo.get("type", "max"))
        
        for restriccion in datos.get("restricciones", []):
            self.añadir_fila_restriccion(default=restriccion)
        
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
