#**LOGITRANS**
*Este es el software modular que diseñé en Python para automatizar, controlar y auditar la operación de una empresa de transportes y 
despachos viales en vivo(CRUD).*

*El sistema está conectado de forma real a una base de datos relacional en MySQL y está dividido en módulos independientes y 
autoejecutables para garantizar los más altos estándares de calidad de software y mantenibilidad del sistema.*

##**requerimientos**
**Gestión Comercial de Clientes:** CRUD completo (Crear, Leer, Actualizar y Eliminar) conectado a MySQL mediante Stored Procedures.
Genera códigos de cliente automáticos y valida que el NIT/Cédula no reciba letras.
**Registro Inteligente de Envíos:** Implementa un calendario interactivo flotante (tkcalendar) para las fechas.
Calcula la tarifa real de despacho automáticamente ($4.000 por Kg base y $800 extra por Kg si la dimensión pasa de 50x50).
**Control de Flota y Asignaciones:** Vinculación Many-to-Many entre conductores y camiones de la empresa, este modulo tambien
contiene la funcion de datetime para recibir el parametro en tiempo real
**Reporte de Emergencias en Ruta:** Línea crítica para siniestros. Bloquea campos vacíos y
despacha alertas con coordenadas GPS calculadas en caliente, tambien cuenta con la funcion datetime
**Manejo de Imágenes con Pillow:** Cuadros visuales en los formularios que cargan, validan formatos (PNG, JPG, GIF) y*
redimensionan las fotos viales en limpio.
**RReportes locales:** Todos los módulos exportan datos,Cada pestaña genera reportes tabulares
independientes a Excel (openpyxl) y reportes profesionales con formato corporativo a PDF (reportlab)
aplicando filtros automáticos.
**Boton de Apariencia Dinámico:** boton en la barra superior para intercambiar la interfaz completa entre Tema Claro y Tema Oscuro.
**Identidad Corporativa:** Ventanas personalizadas con el Favicon oficial de la empresa (imagenes/logitrans_ico.ico).
##**Herramientas y Librerías Utilizadas**
Para correr este proyecto necesitas tener instalado Python, un motor que permita ejecutar script de bases de datos y las siguientes 
librerías:
```bash
pip install mysql-connector-python pillow tkcalendar openpyxl reportlab
```
##**Cómo poner a correr el Software**
*Ejecuta el script SQL en tu MySQL Workbench para levantar las tablas y los Stored Procedures.
Abre el proyecto en tu PyCharm.*
Si quieres probar una pantalla sola de forma aislada, dale clic derecho y pon a correr cada archivo independiente (ej. modulo_cliente.py).
**Para abrir el sistema unificado completo, dale Run al archivo principal:**
```bash
    python main.py
    ```
