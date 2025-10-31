# 🚀 TerraForm: Simulador de Colonización Espacial

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-Academic-orange.svg)]()

> *"La Tierra es un recuerdo. El planeta Lazarus es tu futuro."*

**TerraForm** es una simulación de gestión y supervivencia de colonias espaciales inspirada en *Dwarf Fortress*. Como Director de Colonia en el planeta alienígena Lazarus, deberás equilibrar recursos, asignar tareas estratégicas y guiar a tus colonos especializados a través de crisis y desafíos emergentes.

Este proyecto es una implementación avanzada de **Estructuras de Datos y Algoritmos (EDA)**, utilizando un sistema de **Queue (Cola) + Min-Heap (Montículo Mínimo)** como cerebro del planificador autónomo de tareas.

---

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación](#-instalación)
- [Cómo Jugar](#-cómo-jugar)
- [Arquitectura Técnica](#-arquitectura-técnica)
- [Estructuras de Datos y Algoritmos](#-estructuras-de-datos-y-algoritmos)
- [Colonos Especializados](#-colonos-especializados)
- [Eventos Aleatorios](#-eventos-aleatorios)
- [Documentación Técnica](#-documentación-técnica)
- [Créditos](#-créditos)

---

## ✨ Características Principales

### 🎮 Gestión Indirecta Estratégica
No controlas unidades individuales. Actúas como **Supervisor**: asignas tareas de alto nivel (*Recolectar alimentos*, *Reparar hábitat*, *Explorar terreno*) y la IA de la colonia decide **qué colono especializado** las ejecutará de forma autónoma.

### 🧠 Planificador de Tareas con Prioridad
- **Queue (FIFO)**: Búfer de entrada donde el jugador encola órdenes.
- **Min-Heap**: Cola de prioridad que reordena automáticamente las tareas por urgencia.
- Las tareas críticas (P2: *Reparar hábitat*) **siempre se ejecutan antes** que las de rutina (P5: *Explorar terreno*).

### 👥 Especialistas con POO (Programación Orientada a Objetos)
Cada colono es una **subclase especializada** de `Colono`:
- **Ingeniero**: Experto en reparaciones y construcción.
- **Biólogo**: Maestro en cultivo y curación.
- **Explorador**: Descubre nuevos recursos y ubicaciones.
- **Guardia**: Protege la colonia de amenazas.

El planificador elige al individuo **más eficiente** (aptitud) y **más cercano** (distancia) para cada trabajo.

### 🌍 Mundo Procedural y Dinámico
- **Generación automática** de mapas con biomas, ríos, lagos y zonas de recursos usando ruido Perlin.
- **Ciclo día/noche** que afecta la actividad de los colonos (descansan de 22:00 a 6:00).
- **Eventos aleatorios** que alteran las prioridades y desafían tu gestión.

### 🎨 Interfaz Gráfica Completa
- **Pygame**: Renderizado fluido con sprites animados (mínimo 6 frames por animación).
- **Paneles de información**: Recursos, estado de colonos, tiempo, cola de tareas.
- **Zoom/paneo** del mapa y notificaciones emergentes en tiempo real.

---

## 💻 Requisitos del Sistema

### Software
| Componente | Requisito |
|------------|-----------|
| **Sistema Operativo** | Windows 10/11 (64-bit), macOS 10.15+, Linux (Ubuntu 20.04+) |
| **Python** | 3.8 o superior |
| **Pygame** | 2.0 o superior |

### Hardware

#### Mínimos (Colonias pequeñas)
- **CPU**: Intel Core i3 (2.0 GHz) o AMD Athlon equivalente
- **RAM**: 4 GB
- **GPU**: Gráficos integrados (Intel UHD/Iris Graphics)
- **Almacenamiento**: 100 MB

#### Recomendados (Colonias grandes + efectos visuales)
- **CPU**: Intel Core i5 (2.5 GHz) o AMD Ryzen 5 equivalente
- **RAM**: 8 GB
- **GPU**: Gráficos integrados modernos o tarjeta dedicada básica
- **Almacenamiento**: 100 MB

---

## 🔧 Instalación

### Opción 1: Ejecutar desde el código fuente

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/terraform.git
cd terraform

# 2. Instalar dependencias
pip install pygame

# 3. Ejecutar el juego
python panel_control.py
```

### Opción 2: Ejecutable (si está disponible)
Descarga el archivo `.exe` (Windows) o `.app` (macOS) y ejecuta directamente. No requiere instalación de Python ni Pygame.

---

## 🎮 Cómo Jugar

### Guía Rápida: Tus Primeros 10 Minutos

1. **Pausa el juego**: Presiona `[PAUSAR]` (arriba izquierda) para tener tiempo de pensar.

2. **Revisa tu colonia**:
   - **Panel de Colonos**: Verifica cuántos Ingenieros, Biólogos, Exploradores y Guardias tienes.
   - **Panel de Recursos**: Inicias con 100 de Alimentos, Energía y Materiales.

3. **Asigna tareas iniciales**:
   ```
   [RECURSOS] → [+ Comida] (x2)
   [RECURSOS] → [+ Material] (x1)
   [MANTENIMIENTO] → [+ Energía] (x1)
   ```

4. **Revisa la cola**: El panel `[COLA DE TAREAS]` (abajo derecha) muestra las 4 tareas encoladas.

5. **Reanuda la simulación**: Presiona `[REANUDAR]` y observa cómo tus colonos eligen tareas y se mueven hacia las zonas correspondientes.

### Controles Principales

| Acción | Control |
|--------|---------|
| **Pausar/Reanudar** | Botón `[PAUSAR]` |
| **Velocidad** | Botones `[1x]`, `[2x]`, `[3x]` |
| **Asignar Tareas** | Menús `[MANTENIMIENTO]`, `[RECURSOS]`, `[EXPLORACIÓN]` |
| **Construir** | Botón `[CONSTRUIR]` (requiere Materiales) |
| **Curar Colono** | Botón `[Curar]` en el panel de colonos |
| **Zoom/Paneo** | Teclado (teclas de flecha) |

---

## 🏗️ Arquitectura Técnica

El proyecto sigue una arquitectura modular de **tres capas**:

### 🎨 Capa de Presentación (Frontend/GUI)
- **`panel_control.py`**: Orquestador principal con el bucle de Pygame.
- **`componentes.py`**: Widgets UI (botones, mapa) y generador procedural.
- **`sprite_manager.py`**: Manejo de spritesheets y animaciones.
- **`sistema_notificaciones.py`**: Alertas emergentes.

### ⚙️ Capa de Simulación (Backend/Lógica)
- **`simulador.py`**: **Motor principal** que gestiona el estado del juego, reloj, eventos y el **planificador de tareas**.
- **`colonos.py`**: Modelo POO de entidades (`Colono` + subclases especializadas).
- **`acciones.py`**: Modelo de tareas (`Acción` con prioridad, duración, zona).

### 🧱 Capa Núcleo (Estructuras)
- **`estructuras.py`**: EDAs personalizadas (`Queue`, `Min-Heap`, `Linked-List`).

### Flujo de Datos

```
Usuario (GUI) → Queue (Búfer) → Min-Heap (Prioridad) → Planificador → Colono (Ejecución)
                                                              ↓
                                                    Simulador.ejecutar_ciclo()
```

---

## 🧠 Estructuras de Datos y Algoritmos

### 📥 Flujo de Tareas: Queue + Min-Heap

#### 1. **Queue (Cola FIFO)** - Búfer de Acciones
- **Propósito**: Almacena las órdenes del jugador antes de ser procesadas.
- **Operaciones**: 
  - `encolar(item)` → O(1)
  - `desencolar()` → O(n) *(usando `list.pop(0)`)*
- **Uso**: `simulador.cola_acciones`

#### 2. **Min-Heap (Montículo Mínimo)** - Cola de Prioridad
- **Propósito**: Garantiza que la tarea más urgente sea siempre la primera en ser extraída.
- **Estructura**: Almacena tuplas `(prioridad, Acción)`.
- **Operaciones**:
  - `insertar(prioridad, dato)` → O(log n)
  - `extraer_minimo()` → O(log n)
- **Ventaja**: Elegido sobre una lista ordenada por su eficiencia O(log n) vs O(n).
- **Uso**: `simulador.heap_prioridades`

#### 3. **Linked List (Lista Enlazada)** - Historial de Eventos
- **Propósito**: Almacena el historial de eventos para registro y notificaciones.
- **Operaciones**:
  - `agregar(dato)` → O(n)
  - `obtener_ultimos(n)` → O(n)
- **Uso**: `simulador.historial`

### ⚙️ Algoritmo de Decisión: `encontrar_mejor_colono()`

El núcleo de la IA que asigna tareas a colonos:

```python
# Pseudocódigo simplificado
1. Extraer acción más urgente del Min-Heap (prioridad más baja)
2. Filtrar colonos disponibles (ocupado=False, salud>0, puede_realizar(acción))
3. Para cada colono apto:
   Puntaje = (Aptitud × 100) - (Distancia / 10)
4. Seleccionar el colono con el puntaje más alto
5. Asignar tarea y destino al colono elegido
```

**Fórmula de Puntaje**:
```
Puntaje = (Aptitud × 100) - Penalización_Distancia

Donde:
- Aptitud: Valor de colono.aptitudes.get(accion.tipo, 0.5)
- Penalización_Distancia: distancia_euclidiana / 10
```

**Sistema de Prioridades**:
- **P1**: Emergencias críticas
- **P2**: Reparaciones urgentes
- **P3**: Mantenimiento importante
- **P4**: Recolección de recursos
- **P5**: Exploración de rutina
- **P6**: Tareas opcionales

---

## 👥 Colonos Especializados

Cada colono es una **subclase** de la clase base `Colono` con **aptitudes especializadas**:

| Rol | Especialización | Aptitudes Principales |
|-----|----------------|----------------------|
| 🔧 **Ingeniero** | Construcción y reparación | `reparar_lab`, `reparar_hab`, `construir` (1.0) |
| 🌱 **Biólogo** | Cultivo y curación | `recolectar_comida`, `cultivar`, `curar` (1.0) |
| 🗺️ **Explorador** | Descubrimiento de recursos | `explorar_terreno`, `explorar_cavernas`, `cartografiar` (1.0) |
| 🛡️ **Guardia** | Defensa y seguridad | `defenderse`, `patrullar` (1.0) |

### Herencia y Polimorfismo

```python
Colono (Clase Base)
├── Ingeniero
├── Biologo
├── Explorador
└── Guardia
```

El **planificador** trata a todos los colonos de forma **polimórfica**:
```python
# El simulador no necesita saber el tipo específico
for colono in simulador.colonos:
    if colono.puede_realizar(accion):  # Interfaz común
        puntaje = calcular_eficiencia(colono.aptitudes, accion)
```

---

## 🌩️ Eventos Aleatorios

El planeta Lazarus es impredecible. Sobrevive a:

| Evento | Efectos |
|--------|---------|
| ☄️ **Lluvia de Meteoritos** | Daño severo a colonos, hábitats y laboratorios |
| ⚡ **Tormenta Electromagnética** | Daño moderado a colonos, daño crítico a laboratorios |
| 🌡️ **Caída de Temperatura** | Pérdida de energía y salud de colonos |
| 🌍 **Terremoto** | Daño masivo a colonos y hábitats |
| 🚀 **Llegada de Nuevos Colonos** | +3 colonos con roles aleatorios |

**Comportamiento del Sistema**:
- Los eventos generan **tareas de alta prioridad** (P2) automáticamente.
- Ejemplo: Un *Terremoto* crea tareas `reparar_hab` que **saltan la fila** en el Min-Heap.

---

## 📚 Documentación Técnica

### Para Desarrolladores

El proyecto incluye documentación detallada para desarrolladores:

- **`DOCUMENTO TECNICO PARA DESARROLLADORES final2.pdf`**:
  - Arquitectura completa del sistema
  - Detalles de implementación de EDAs (Queue, Min-Heap, Linked-List)
  - API de módulos (`simulador.py`, `colonos.py`, `acciones.py`)
  - Algoritmos de decisión y movimiento
  - Diagramas UML (clases y estados)
  - Plan de pruebas y métricas de rendimiento

### Para Usuarios

- **`DOCUMENTO PARA CLIENTE.pdf`**:
  - Guía de uso completa
  - Explicación del flujo de tareas
  - Descripción de la interfaz (paneles, botones, logs)
  - FAQ y resolución de problemas comunes
  - Roadmap de funcionalidades futuras

---

## 🚧 Limitaciones Conocidas

- **No hay control directo de unidades**: Solo puedes asignar tareas a la colonia, no a colonos individuales.
- **Construcción en sitios predefinidos**: No puedes elegir dónde construir libremente.
- **Sin pathfinding**: Los colonos se mueven en línea recta y pueden atascarse en obstáculos (ríos, montañas).
- **Combate abstracto**: Los eventos de defensa aplican daño directo, sin combate visual.
- **Necesidades simplificadas**: No hay hambre/sed/sueño individuales por colono.
- **Sin Game Over explícito**: La simulación continúa incluso si pierdes todos los colonos.

---

## 🔮 Roadmap / Mejoras Futuras

### Planeadas para versiones futuras:

- 🗺️ **Pathfinding (A\*)**: Navegación inteligente rodeando obstáculos.
- 🧑‍🚀 **Sistema de Necesidades Individuales**: Hambre, energía y ocio por colono.
- 📈 **Árbol de Habilidades**: Los colonos ganan XP y suben de nivel.
- 🦖 **Fauna Hostil y Combate**: Criaturas alienígenas que atacan la base.
- 🔬 **Sistema de Investigación**: Desbloqueo de tecnologías avanzadas.
- 🏗️ **Construcción Libre**: Diseña el trazado de tu base.
- ⚙️ **Cadenas de Producción (Crafting)**: Mineral → Lingote → Herramienta.
- 🏆 **Condiciones de Victoria**: Objetivos claros y pantalla de Game Over.

---

## 🎓 Créditos

**Proyecto Académico**  
*Materia: Estructura de Datos y Algoritmos II*  
*Profesor: Ricardo Tachiquin Guitierrez*

**Equipo de Desarrollo**:
- Bruno Rueda Betancourt
- Jose Pablo Garcia Zamudio
- Luis Jaime Enriquez Martinez

---

## 📄 Licencia

Este es un proyecto académico desarrollado para fines educativos.

---

## 🙏 Agradecimientos

Inspirado en la profundidad de *Dwarf Fortress* y la elegancia de las estructuras de datos clásicas.

---

**¿Listo para colonizar Lazarus?** 🌍✨

```bash
python panel_control.py
```

*"En el vacío del espacio, solo la planificación y la adaptación garantizan la supervivencia."*
