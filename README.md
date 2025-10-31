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


Estructura,Propósito,Operaciones Clave,Complejidad,Uso en el Sistema
Queue (Cola),"Búfer de entrada para las órdenes del jugador (FIFO)[cite: 395, 526].",encolar() y desencolar()[cite: 475].,O(1) y O(n)[cite: 527].,simulador.cola_acciones[cite: 528].
Min-Heap,"Cola de Prioridad central (extrae siempre la más urgente)[cite: 394, 531].","insertar() y extraer_minimo()[cite: 473, 531].",O(logn)[cite: 531].,simulador.heap_prioridades[cite: 532].
Linked List,"Almacenamiento del historial de eventos y notificaciones[cite: 534, 336].",agregar()[cite: 535].,O(n)[cite: 535].,simulador.historial[cite: 536].
