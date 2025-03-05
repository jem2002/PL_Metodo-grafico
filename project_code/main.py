import optimizar as opt

if __name__ == "__main__":
    objetivo = {
        'coeficiente': [3, 2],  # Z = 3x + 2y
        'tipo': 'max'      # 'max' o 'min'
    }
    
    restricciones = [
        {'a': 2, 'b': 1, 'c': 20, 'inecuacion': '<='},
        {'a': 1, 'b': 2, 'c': 20, 'inecuacion': '<='},
        {'a': 1, 'b': 0, 'c': 0, 'inecuacion': '>='},  # x >= 0
        {'a': 0, 'b': 1, 'c': 0, 'inecuacion': '>='},  # y >= 0
    ]
    
    opt.resolver_problema_optimizacion(objetivo, restricciones)