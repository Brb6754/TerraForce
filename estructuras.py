class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.tamano = 0
    
    def agregar(self, dato):
        nuevo_nodo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self.tamano += 1
    
    def obtener_ultimos(self, n):
        elementos = []
        actual = self.cabeza
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos[-n:] if len(elementos) > n else elementos

class Queue:
    def __init__(self):
        self.items = []
    
    def encolar(self, item):
        self.items.append(item)
    
    def desencolar(self):
        if not self.esta_vacia():
            return self.items.pop(0)
        return None
    
    def esta_vacia(self):
        return len(self.items) == 0
    
    def tamano(self):
        return len(self.items)

class MonticuloMinimo:
    def __init__(self):
        self.heap = []
    
    def padre(self, i): return (i - 1) // 2
    def hijo_izq(self, i): return 2 * i + 1
    def hijo_der(self, i): return 2 * i + 2
    
    def insertar(self, prioridad, dato):
        self.heap.append((prioridad, dato))
        self._subir(len(self.heap) - 1)
    
    def _subir(self, i):
        while i > 0:
            p = self.padre(i)
            if self.heap[i][0] < self.heap[p][0]:
                self.heap[i], self.heap[p] = self.heap[p], self.heap[i]
                i = p
            else:
                break
    
    def extraer_minimo(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()[1]
        minimo = self.heap[0][1]
        self.heap[0] = self.heap.pop()
        self._bajar(0)
        return minimo
    
    def _bajar(self, i):
        while True:
            menor = i
            izq = self.hijo_izq(i)
            der = self.hijo_der(i)
            if izq < len(self.heap) and self.heap[izq][0] < self.heap[menor][0]:
                menor = izq
            if der < len(self.heap) and self.heap[der][0] < self.heap[menor][0]:
                menor = der
            if menor != i:
                self.heap[i], self.heap[menor] = self.heap[menor], self.heap[i]
                i = menor
            else:
                break
    
    def esta_vacio(self): return len(self.heap) == 0
    def tamano(self): return len(self.heap)