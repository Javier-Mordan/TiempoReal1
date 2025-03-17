# Monitoreo de Señales de Drones en Tiempo Real ¨Video: https://youtu.be/BgHuQZwtFtI¨ 

El proyecto tiene como objetivo desarrollar un sistema en tiempo real para monitorear las señales provenientes de drones, procesarlas y mostrar alertas cuando se superen límites específicos, como la altitud máxima permitida. Además, el sistema permite visualizar en una interfaz gráfica los datos de las señales en tiempo real, como la altitud y velocidad del dron.  

Utilizando conceptos de **Programación en Tiempo Real (PTR)**, se implementan **semáforos** para asegurar la sincronización de hilos y evitar problemas como las condiciones de carrera en el acceso concurrente a la base de datos.  

---

## Diseños y Arquitecturas  

### Base de Datos  

La base de datos está diseñada con tres tablas principales:  

#### `drone_signals`  
Almacena las señales del dron, incluyendo:  
- `id`: Identificador único de la señal.  
- `timestamp`: Fecha y hora en que se registró la señal.  
- `altitude`: Altitud en metros del dron.  
- `speed`: Velocidad en metros por segundo del dron.  
- `processed`: Estado de procesamiento de la señal.  

#### `control_signals`  
Guarda información sobre los valores de control y correcciones aplicadas:  
- `id`: Identificador único del valor de control.  
- `timestamp`: Fecha y hora de generación del valor de control.  
- `control_value`: Valor de control recibido.  
- `correction`: Corrección aplicada (si es necesaria).  

#### `errors`  
Registra errores durante el procesamiento de señales:  
- `id`: Identificador único del error.  
- `timestamp`: Fecha y hora del error.  
- `error_message`: Descripción del error.  

Estas relaciones permiten la captura, el procesamiento y el registro de alertas de manera estructurada.  

---

## Arquitectura de la Aplicación  

El sistema está dividido en varias capas:  

1. **Captura de señales**  
   - Un hilo independiente simula la captura de señales del dron.  
   - Se generan aleatoriamente valores de altitud y velocidad.  
   - Los datos se almacenan en la base de datos.  
   - Se ejecuta cada segundo.  

2. **Procesamiento de señales**  
   - Un segundo hilo procesa las señales almacenadas.  
   - Se aplican ajustes a los valores de altitud y velocidad.  
   - Se marcan los registros como procesados.  
   - Se registran los errores en la tabla correspondiente.  

3. **Interfaz gráfica (UI)**  
   - Creada con Tkinter.  
   - Muestra en tiempo real las señales capturadas y procesadas.  
   - Se actualiza cada 2 segundos.  

4. **Sincronización**  
   - Se usa un **semáforo** para evitar problemas de concurrencia.  
   - Solo un hilo puede acceder a la base de datos a la vez.  

---

## Problemas a Resolver  

### 1. Sincronización de Acceso a la Base de Datos  
El principal desafío es garantizar el acceso seguro a la base de datos desde múltiples hilos.  
- Se usa un **semáforo** para evitar **condiciones de carrera**.  
- Las funciones clave (`capture_drone_signal`, `process_drone_signal`, `log_error`) adquieren y liberan el semáforo al interactuar con la base de datos.  

### 2. Alertas de Altitud  
Si la altitud de una señal **supera los 80 metros**, el sistema:  
- Muestra una alerta visual con `messagebox` de Tkinter.  
- Registra el evento en la base de datos.  

### 3. Procesamiento de Datos  
- Se aplican **ajustes** del 5% a la altitud y del 2% a la velocidad.  
- Se simula un ajuste de los datos antes de ser marcados como procesados.  
- Se registran errores en caso de fallos durante este proceso.  

---

## Implementación de Semáforos  

La sincronización de hilos es un aspecto clave en la **Programación en Tiempo Real**.  

- Se usa un **semáforo** para controlar el acceso concurrente a la base de datos SQLite.  
- Tanto el hilo de captura como el de procesamiento necesitan acceso exclusivo.  
- Implementación:  
  ```python
  semaphore.acquire()  # Adquirir acceso exclusivo
  # Código que interactúa con la base de datos
  semaphore.release()  # Liberar acceso
