🚀 TerraForm: Simulador de Colonización Espacial
TerraForm es una simulación de gestión y supervivencia de una colonia espacial en el planeta alienígena Lazarus. Inspirado en juegos como Dwarf Fortress, el jugador asume el rol de Director de Colonia y gestiona las necesidades de su asentamiento a través de directivas de alto nivel, no mediante el control directo de unidades.

El proyecto es una implementación avanzada de Estructuras de Datos y Algoritmos (EDA), utilizando una Queue (Cola) y un Min-Heap (Montículo Mínimo) como el cerebro de la inteligencia artificial del planificador de tareas.

✨ Características Principales
- Gestión Indirecta: Eres un Supervisor. Asigna tareas estratégicas como Recolectar alimentos o Reparar hábitat, y la IA de la colonia decide qué colono especializado y disponible (Biólogo, Ingeniero, etc.) las ejecutará de forma autónoma.
- Planificador de Tareas con Prioridad: El sistema utiliza una Queue para las órdenes del jugador y un Min-Heap para reordenarlas automáticamente por urgencia. Las tareas críticas (ej. Reparar hábitat - Prioridad 2) se atienden antes que las de rutina (ej. Explorar terreno - Prioridad 5).
- Especialistas con POO: Cada colono es una subclase de Colono (Ingeniero, Biólogo, Explorador, Guardia) con aptitudes especializadas, lo que permite al planificador elegir al individuo más eficiente para cada trabajo (Programación Orientada a Objetos).
- Eventos Aleatorios: Sobrevive a crisis como Lluvias de Meteoritos, Tormentas Electromagnéticas o Terremotos, que generan tareas de reparación urgentes y añaden un desafío constante.
- Mapa y Simulación Procedural: El mundo de Lazarus se genera automáticamente e incluye biomas, ríos, cultivos, hábitats y laboratorios, con un ciclo de día y noche que afecta la actividad de los colonos.

💻 Requisitos del Sistema
TerraForm está diseñado para ser compatible con la mayoría de los sistemas operativos modernos.
Requisitos de Software 
Sistema Operativo: Windows 10/11 (64-bit), macOS (10.15+), o Linux (Ubuntu 20.04+).
Ejecución desde el código fuente:
- Python: 3.8 o superior.
- Biblioteca: Pygame 2.0 o superior.


🧠 Estructuras de Datos y Algoritmos (EDA)
El núcleo lógico de TerraForm reside en un conjunto de Estructuras de Datos y Algoritmos (EDA) personalizados que orquestan el flujo de tareas y la toma de decisiones de la colonia.
📥 Flujo de Tareas: 

Queue y Min-Heap
El sistema de planificación utiliza dos estructuras principales para gestionar las órdenes del jugador y las prioridades de la colonia
- Queue (Cola) - Búfer de Acciones:
  Propósito: Sirve como el búfer de entrada (FIFO) donde el jugador encola las tareas (órdenes) a través de la interfaz (GUI).
  Rol: Almacena las tareas antes de que el planificador las procese.
  Comportamiento: Las órdenes se atienden por orden de llegada, pero aún no están priorizadaS


- Min-Heap (Montículo Mínimo) - Cola de Prioridad:
  Propósito: Es la cola de prioridad central que garantiza que la tarea más urgente sea siempre la primera en ser extraída666666666666.
  Rol: Almacena tuplas (prioridad, Acción), ordenando automáticamente las tareas por su valor de prioridad7777.
  Eficiencia: Se eligió sobre una lista ordenada porque el Heap asegura una inserción y extracción de tareas priorizadas de forma óptima O(log n)



-⚙️ Algoritmo de Decisión (Asignación de Colonos)
El algoritmo simulador.encontrar_mejor_colono() es el corazón de la IA y determina quién realiza qué tarea:
  Extracción Prioritaria: El planificador extrae la acción más urgente (el valor de prioridad más bajo) del Min-Heap10.
  Filtro de Disponibilidad: Se evalúa a todos los colonos que estén disponibles (ocupado = False) y que sean aptos para realizar el tipo de acción requerida11.
  Cálculo de Puntaje (Eficiencia): A cada colono apto se le asigna un puntaje basado en su Aptitud y su proximidad a la zona de la tarea
  Se selecciona el colono con el puntaje más alto, lo que garantiza que se elija al colono más eficiente y más cercano para la tarea13.
