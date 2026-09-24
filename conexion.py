# conexion.py - PARTE 1
import mysql.connector
from mysql.connector import Error

class ConexionLOGITRANS:
    # Acceso a la base de datos de logitrans

    def __init__(self):
        # Configuración de conexion mysql
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'admin',
            'database': 'logitrans'
        }

    def conectar(self):
        # Establece y devuelve la conexion
        try:
            conn = mysql.connector.connect(**self.config)
            if conn.is_connected():
                return conn
        except Error as e: # Renombramos el error que dirige el sistema para que aparezca cuando imprimamos el mensaje
            print(f"Error: No se pudo conectar a la base de datos: {e}")
            return None

    # Procedimientos almacenados
    def sp_insertar_cliente(self, datos): # datos es la caja contenedora que va a traer toda la info de la db
        # Conectamos primero con la db
        conn = self.conectar()
        # si no conecta, retorna error
        if not conn:
            return False, "Error de conexion."
        try:
            # Creamos el cursor o mensajero, quien se encarga de enviar los datos (intermediario)
            cursor = conn.cursor()
            # Argumentos exactos solicitados por el procedimiento
            args = (
                datos['codigo_unico'], datos['tipo_cliente'], datos['nombre_o_razon_social'],
                datos['rut_o_dni'], datos['direccion_fiscal'], datos['direccion_recogida'],
                datos['telefono'], datos['email'], datos['persona_contacto'],
                datos['termino_pago'], datos['clasificacion_por_envio']
            )
            cursor.callproc('sp_InsertarCliente', args) # llamamos y ejecutamos el procedimiento almacenado
            conn.commit() # Commit de la transaccion, guardar los cambios
            cursor.close() # Cerramos el cursor (intermediario)
            conn.close() # Cerramos la conexion
            return True, "¡Operación Exitosa!\nEl cliente ha sido registrado mediante Stored Procedure."
        except Error as e:
            return False, f"Falla en la transacción: {e}"

    def sp_eliminar_cliente(self, cliente_id): # llamamos al cliente porque se elimina por medio del id
        conn = self.conectar() # conectar a la db
        if not conn:
            return False, "Error de conexion, intenta de nuevo."

        try:
            cursor = conn.cursor() # llamamos al cursor (intermediario)
            cursor.callproc('sp_EliminarCliente', (cliente_id,)) # llamamos el procedimiento
            conn.commit() # Guardamos cambios
            cursor.close() # cerramos cursor (intermediario)
            conn.close() # cerramos conexion
            return True, "Registro eliminado correctamente del sistema."
        except Error as e:
            # Captura el SIGNAL SQLSTATE '45000' que programamos ante envíos existentes
            return False, f"Restricción de Calidad: {e}"

    def sp_actualizar_cliente(self, datos): # Actualizar datos de cliente
        conn = self.conectar() # llamamos la conexion
        if not conn:
            return False, "Error de conexión, intenta de nuevo."
        try:
            cursor = conn.cursor() # creamos el cursor(intermediario)
            args = (
                datos['cliente_id'], datos['tipo_cliente'], datos['nombre_o_razon_social'],
                datos['rut_o_dni'], datos['direccion_fiscal'], datos['telefono'],
                datos['email'], datos['persona_contacto']
            ) # Pasamos los argumentos modificables
            cursor.callproc('sp_ActualizarCliente', args)  # Llamado al procedimiento almacenado
            # y le pasamos los argumentos
            conn.commit()  # Guardamos los cambios permanentemente
            cursor.close() # Cerramos cursor (intermediario)
            conn.close() # Cerramos la conexion
            return True, "¡Cambios guardados con éxito!"
        except Error as e:
            return False, f"Falla en la actualización: {e}"

    def sp_insertar_envio(self, datos):
        conn = self.conectar()
        if not conn:
            return False, "Error de conexion."
        try:
            cursor = conn.cursor()
            args = (
                datos['numero_guia'], datos['fecha_hora_recepcion'], datos['id_cliente'],
                datos['remitente'], datos['destinatario'], datos['direccion_origen'],
                datos['direccion_destino'], datos['tipo_servicio'], datos['descripcion_contenido'],
                datos['peso'], datos['dimensiones'], datos['valor_declarado'],
                datos['costo'], datos['forma_pago'], datos['estado_actual'],
                datos['instrucciones_especiales'], datos['ruta_distribucion']
            )
            cursor.callproc('sp_InsertarEnvio', args)
            conn.commit()
            cursor.close()
            conn.close()
            return True, "¡Guía de Distribución generada con éxito!"
        except Error as e:
            return False, f"Falla al insertar envío: {e}"

    def sp_obtener_todos_envios(self):
        conn = self.conectar()
        if not conn:
            return False, "Error de conexion"
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_ObtenerTodosEnvios')  # llamar al procedimiento

            resultados = [] # Ponemos los resultados de los envios guardados en la database en una lista vacia
            for result in cursor.stored_results(): # Iteramos cada resultado para mostrarlo
                resultados = result.fetchall() # trae toda la consulta mysql y la cuarda en la lista vacia resultados
            cursor.close() # Cerramos el cursor para liberar memoria
            conn.close()
            return resultados  # retornamos la lista que se extrajo de la db
        except Error as e:
            print(f"Error al leer envíos: {e}")
            return []

    def sp_asignar_conductor_vehiculo(self, conductor_id, vehiculo_id):
        conn = self.conectar()
        if not conn:
            return False, "Error de conexion."
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_AsignarConductorVehiculo', (conductor_id, vehiculo_id))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Recursos asociados correctamente"
        except Error as e:
            return False, f"Falla de asignación: {e}"

    def sp_obtener_monitoreo_flota(self):
        conn = self.conectar()
        if not conn:
            return False, "Error de conexion"
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_ObtenerMonitoreoFlota') # Aqui es donde llamamos el stored
            # procedure tal como esta en la db

            resultados = []
            for result in cursor.stored_results():
                resultados = result.fetchall()
            cursor.close()
            conn.close()
            return resultados
        except Error as e:
            print(f"Error al leer monitoreo de flota: {e}")
            return []

    def sp_insertar_incidente(self, datos):
        conn = self.conectar()
        if not conn:
            return False, "Error de conexion."
        try:
            cursor = conn.cursor()
            args = (
                datos['vehiculo_id'], datos['conductor_id'], datos['codigo'],
                datos['fecha_hora'], datos['tipo_incidente'], datos['ubicacion'],
                datos['descripcion'], datos['causas'], datos['consecuencias'],
                datos['medidas_tomadas'], datos['estado_resolucion']
            )
            cursor.callproc('sp_InsertarIncidente', args)
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Alerta roja de siniestro reportada a la central de despacho."
        except Error as e:
            return False, f"Error al emitir alerta: {e}"

    def sp_obtener_incidentes_activos(self):
        conn = self.conectar()
        if not conn:
            return False, "error de conexion."
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_ObtenerIncidentesActivos')

            resultados = [] # Lista vacia para guardar el iterable de abajo
            for result in cursor.stored_results():
                resultados = result.fetchall()
            cursor.close()
            conn.close()
            return resultados
        except Error as e:
            print(f"Error al leer incidentes: {e}")
            return []


# Realizar la prueba de conexion unicamente en este modulo conexion
if __name__ == '__main__':
    print("Iniciando prueba de conexión con la Base de Datos Logitrans...")

    test = ConexionLOGITRANS()
    #Test de conexión a MySQL
    enlace = test.conectar()
    if enlace and enlace.is_connected(): # llamamos a la funcion is_conected para verificar que la conexion en myqsl
        # Funciona correctamente
        print("Conexion establecida de forma correcta")
        enlace.close() # Cerramos la conexion
    else:
        print("Error: No se pudo establecer la conexión física.")
        exit()



