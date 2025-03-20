import customtkinter as ctk
import tkinter as tk
import json
import os
import google.generativeai as genai
from optimizacion import resolver_optimizacion
from grafica import dibujar_grafico
import re
import ast
import operator as op

# Operadores permitidos para la evaluación segura
operadores_permitidos = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
}

def evaluar_expresion_segura(expr):
    """
    Evalúa una expresión matemática de manera segura.
    Solo permite números y operaciones básicas.
    """
    def _evaluar_nodo(nodo):
        if isinstance(nodo, ast.Expression):
            return _evaluar_nodo(nodo.body)
        elif isinstance(nodo, ast.Constant):  # Python 3.8+
            return nodo.value
        elif isinstance(nodo, ast.Num):  # Python < 3.8
            return nodo.n
        elif isinstance(nodo, ast.BinOp):
            return operadores_permitidos[type(nodo.op)](
                _evaluar_nodo(nodo.left), _evaluar_nodo(nodo.right)
            )
        elif isinstance(nodo, ast.UnaryOp):
            return operadores_permitidos[type(nodo.op)](_evaluar_nodo(nodo.operand))
        else:
            raise ValueError(f"Operación no permitida: {type(nodo).__name__}")
    
    try:
        # Parsear la expresión en un árbol de sintaxis abstracta (AST)
        arbol = ast.parse(expr, mode='eval')
        return _evaluar_nodo(arbol.body)
    except (SyntaxError, ValueError, TypeError):
        raise ValueError(f"Expresión no válida: {expr}")

class FilaDeRestricciones(ctk.CTkFrame):
    def __init__(self, master, n_variables, **kwargs):
        super().__init__(master, **kwargs)
        self.n_variables = n_variables
        self.entries_a = []
        for i in range(n_variables):
            entry = ctk.CTkEntry(self, width=50, placeholder_text=f"a{i+1}")
            entry.grid(row=0, column=i, padx=5, pady=5)
            self.entries_a.append(entry)
        
        # Selector de desigualdad antes del input c
        self.var_ineq = ctk.StringVar(value="<=")
        self.dropdown = ctk.CTkOptionMenu(self, values=["<="], variable=self.var_ineq, width=70)
        self.dropdown.grid(row=0, column=n_variables, padx=5, pady=5)
        
        # Input c después del selector de desigualdad
        self.entry_c = ctk.CTkEntry(self, width=50, placeholder_text="c")
        self.entry_c.grid(row=0, column=n_variables+1, padx=5, pady=5)
        
    def obtener_restriccion(self):
        try:
            # Evaluar los coeficientes a
            a = [evaluar_expresion_segura(entry.get()) for entry in self.entries_a]
            # Evaluar el término independiente c
            c = evaluar_expresion_segura(self.entry_c.get())
            ineq = self.var_ineq.get()
            return {'a': a, 'c': c, 'inecuacion': ineq}
        except ValueError as e:
            print(f"Error al evaluar la expresión: {e}")
            return None

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Método Simplex")
        self.geometry("1000x600")
        
        # Configurar las columnas
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2) 
        self.rowconfigure(0, weight=1)
        
        # Frame izquierdo
        self.frame_left = ctk.CTkFrame(self, width=300)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # Se expande en todas direcciones

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
        
        # Frame derecho que ocupa el espacio restante
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")  # Se expande en todas las direcciones

        # Dividir el frame_right en dos partes
        self.frame_top = ctk.CTkFrame(self.frame_right, height=300)
        self.frame_top.pack(fill="both", expand=True)

        self.frame_bottom = ctk.CTkFrame(self.frame_right, height=300)
        self.frame_bottom.pack(fill="both", expand=True)

        # Inicializar el número de variables
        self.n_variables = 0  # Valor predeterminado
        self.cambiar_modo()

    def construir_modo_manual(self):
        self.label_n_variables = ctk.CTkLabel(self.frame_left, text="Número de Variables de Decisión", anchor="w")
        self.label_n_variables.pack(pady=5)
        
        self.entry_n_variables = ctk.CTkEntry(self.frame_left, width=50, placeholder_text="n")
        self.entry_n_variables.pack(pady=5)
        
        self.button_set_n = ctk.CTkButton(self.frame_left, text="Establecer Número de Variables", command=self.establecer_n_variables)
        self.button_set_n.pack(pady=5)
        
        self.label_obj = ctk.CTkLabel(self.frame_left, text="Función Objetivo (Z = a1x1 + a2x2 + ... + anxn)")
        self.label_obj.pack(pady=5)
        
        self.frame_obj = ctk.CTkFrame(self.frame_left, height=30)
        self.frame_obj.pack(pady=5)
        
        self.entries_obj = []
        
        self.var_obj_type = ctk.StringVar(value="max")
        self.dropdown_obj_type = ctk.CTkOptionMenu(self.frame_left, values=["max", "min"], variable=self.var_obj_type, width=80)
        self.dropdown_obj_type.pack(pady=5)
        
        self.label_constraints = ctk.CTkLabel(self.frame_left, text="Restricciones (inecuaciones)")
        self.label_constraints.pack(pady=5)
        
        # Contenedor scrollable para las restricciones
        self.scrollable_frame = ctk.CTkScrollableFrame(self.frame_left, height=60)  # Altura inicial de 60
        self.scrollable_frame.pack(pady=5, fill="both", expand=True)
        
        self.frame_constraints = ctk.CTkFrame(self.scrollable_frame)
        self.frame_constraints.pack(fill="both", expand=True)
        
        self.filas_restricciones = []
        
        # Frame para contener los botones de añadir y eliminar
        self.frame_botones = ctk.CTkFrame(self.frame_left)
        self.frame_botones.pack(pady=5, fill="x")
        
        self.button_add = ctk.CTkButton(self.frame_botones, text="+ Añadir Restricción", command=self.añadir_fila_restriccion)
        self.button_add.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        self.button_remove = ctk.CTkButton(self.frame_botones, text="- Eliminar Última Restricción", command=self.remover_fila_restriccion)
        self.button_remove.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        self.button_solve = ctk.CTkButton(self.frame_left, text="Resolver Optimización", command=self.resolver)
        self.button_solve.pack(pady=10, fill="x")
        
        self.text_output = ctk.CTkTextbox(self.frame_left, height=40)
        self.text_output.pack(pady=5, fill="both", expand=True)

    def establecer_n_variables(self):
        try:
            self.n_variables = int(self.entry_n_variables.get())
            if self.n_variables < 1:
                raise ValueError("El número de variables debe ser al menos 1")
            self.actualizar_entradas_objetivo()
            self.text_output.insert(tk.END, f"Número de variables establecido en {self.n_variables}\n")
        except ValueError as e:
            self.text_output.insert(tk.END, f"Error: {str(e)}\n")

    def actualizar_entradas_objetivo(self):
        for widget in self.frame_obj.winfo_children():
            widget.destroy()
        self.entries_obj = []
        for i in range(self.n_variables):
            label = ctk.CTkLabel(self.frame_obj, text=f"a{i+1}:")
            label.grid(row=0, column=i*2, padx=5, pady=5)
            entry = ctk.CTkEntry(self.frame_obj, width=50)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.entries_obj.append(entry)

    def construir_modo_texto(self):
        self.texto_problema = ctk.CTkTextbox(
            self.frame_texto, 
            height=100,
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
            self.actualizar_datos_interfaz(resultado)
            self.modo_entrada.set("Modo Manual")
            self.text_output.insert(tk.END, "Datos cargados exitosamente\n")
            
        except json.JSONDecodeError:
            self.text_output.insert(tk.END, "Error: Formato JSON inválido en la respuesta\n")
        except KeyError as e:
            self.text_output.insert(tk.END, f"Error: Faltan datos en la respuesta - {str(e)}\n")
        except Exception as e:
            self.text_output.insert(tk.END, f"Error: {str(e)}\n")

    def llamar_api_ia(self, texto):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API key no configurada. Establece GOOGLE_API_KEY en tus variables de entorno")
        
        genai.configure(api_key=api_key)

        prompt = f"""
        Transforma el siguiente problema de programación lineal a formato JSON estricto usando EXACTAMENTE esta estructura:
        
        {{
            "objetivo": {{
                "coeff": [a1, a2, ..., an],
                "type": "max"|"min"
            }},
            "restricciones": [
                {{
                    "a": [a1, a2, ..., an],
                    "c": número,
                    "inecuacion": "<="|">="
                }}
            ]
        }}
        
        Reglas CRÍTICAS:
        1. Variables deben ser x1, x2,... xn en orden
        2. Convertir todas las inecuaciones a forma estándar:
        - Expresiones con <= permanecen igual
        - Expresiones con >= se invierte la desigualdad multiplicando por -1
        3. Eliminar restricciones redundantes o inválidas
        4. Ignorar restricciones con todos los coeficientes en 0
        5. Normalizar tipo de objetivo: "max" o "min"
        6. Coeficientes deben ser numéricos (incluyendo negativos)
        
        Ejemplos válidos:
        * "3x + 2y ≤ 10" -> {{"a": [3,2], "c":10, "inecuacion": "<="}}
        * "x1 - 4x2 ≥ 5" -> {{"a": [1,-4], "c":5, "inecuacion": ">="}}
        
        Problema a analizar:
        {texto}
        
        Devuelve SOLO el JSON válido sin comentarios.
        """
        
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            
            # Extraer JSON de la respuesta
            json_str = response.text
            json_str = json_str[json_str.find('{'):json_str.rfind('}')+1]
            json_str = json_str.replace('`', '')
            
            datos = json.loads(json_str)
            
            # Validar estructura
            if not self.validar_respuesta_ia(datos):
                raise ValueError("Estructura JSON inválida")
                
            return datos
            
        except Exception as e:
            raise ValueError(f"Error en Gemini: {str(e)}")

    def validar_respuesta_ia(self, datos):
        required_keys = {'objetivo', 'restricciones'}
        if not required_keys.issubset(datos.keys()):
            return False
        
        obj = datos['objetivo']
        if 'coeff' not in obj or 'type' not in obj:
            return False
        if obj['type'] not in ('max', 'min'):
            return False
        
        for r in datos['restricciones']:
            if 'a' not in r or 'c' not in r or 'inecuacion' not in r:
                return False
            if r['inecuacion'] not in ('<=', '>='):
                return False
                
        return True
    
    def actualizar_datos_interfaz(self, datos):
        try:
            # Actualizar número de variables basado en los coeficientes del objetivo
            n_vars = len(datos["objetivo"]["coeff"])
            self.entry_n_variables.delete(0, tk.END)
            self.entry_n_variables.insert(0, str(n_vars))
            self.establecer_n_variables()
            
            # Actualizar función objetivo
            objetivo = datos["objetivo"]
            for i in range(n_vars):
                self.entries_obj[i].delete(0, tk.END)
                self.entries_obj[i].insert(0, str(objetivo["coeff"][i]))
            self.var_obj_type.set(objetivo["type"])
            
            # Limpiar restricciones existentes
            while self.filas_restricciones:
                self.remover_fila_restriccion()
            
            # Añadir nuevas restricciones con validación
            for r in datos["restricciones"]:
                if len(r["a"]) != n_vars:
                    continue  # Ignorar restricciones incompatibles
                self.añadir_fila_restriccion(default=r)
                
        except Exception as e:
            raise ValueError(f"Error actualizando interfaz: {str(e)}")

    def añadir_fila_restriccion(self, default=None):
        if not hasattr(self, 'n_variables') or self.n_variables == 0:
            self.text_output.insert(tk.END, "Error: Establece el número de variables primero.\n")
            return
        
        fila = FilaDeRestricciones(self.frame_constraints, self.n_variables)
        fila.pack(pady=2)
        if default:
            for i, a in enumerate(default['a']):
                fila.entries_a[i].insert(0, str(a))
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
            coeff_obj = [float(entry.get()) for entry in self.entries_obj]
        except ValueError:
            self.text_output.insert(tk.END, "Error en los coeficientes de la función objetivo.\n")
            return
        objetivo = {'coeff': coeff_obj, 'type': self.var_obj_type.get()}
        
        restricciones = []
        for fila in self.filas_restricciones:
            restriccion = fila.obtener_restriccion()
            if restriccion is None:
                self.text_output.insert(tk.END, "Error en los datos de alguna restricción.\n")
                return
            restricciones.append(restriccion)
        
        # Resolver el problema usando el método simplex
        resultado, mensaje, puntos_factibles, tablas_simplex = resolver_optimizacion(objetivo, restricciones)
        self.text_output.insert(tk.END, mensaje + "\n")
        
        if resultado is None:
            return
        print(tablas_simplex)
        dibujar_grafico(restricciones, puntos_factibles, resultado['punto_optimo'], self.frame_right)