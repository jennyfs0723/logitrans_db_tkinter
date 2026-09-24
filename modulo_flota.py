# importamos modulos
import tkinter as tk
from tkinter import ttk, messagebox
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Creamos la clase de ModuloFlota
class ModuloFlota:

# inicializamos los atributos
    def __init__(self, contenedor, conexion_db):
        self.contenedor = contenedor # Contenedor, pantalla donde mostramos datos
        self.db = conexion_db # Conexion a la db
        self.inicializar_componentes() # Comando para inicializar los componentes
        self.cargar_tabla_visual() # lo llamamos para cargar tabla
    #Definimos la variable para inicializar componentes
    def inicializar_componentes(self):
        # Creamos el frame izquierdo
        self.lf_flota = tk.LabelFrame(self.contenedor, text=" Asignación de Recursos de Transporte ", padx=15, pady=15,
                                      font=("Arial", 10, "bold"))
        self.lf_flota.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)

        # Entrada de datos y creacion del lablel
        tk.Label(self.lf_flota, text="ID Vehículo (numero):").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_vehiculo = tk.Entry(self.lf_flota, width=20)
        self.ent_vehiculo.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_flota, text="ID Conductor (Número):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_conductor = tk.Entry(self.lf_flota, width=20)
        self.ent_conductor.grid(row=1, column=1, pady=5, padx=5, sticky="w")

        # Create en la tabla intermedia conductor-vehiculo
        # Creacion de boton
        self.btn_vincular = tk.Button(
            self.lf_flota,
            text="Vincular Conductor y Vehiculo",
            command=self.ejecutar_vinculacion_flota,
            bg="#2980B9",
            fg="white",
            font=("Arial", 10, "bold")
        )
        # darle dimensiones al boton
        self.btn_vincular.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")

        #Creacion de botones para exportar pdf y excel
        frame_exportar_directo = tk.Frame(self.lf_flota, pady=5)
        frame_exportar_directo.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.btn_excel = tk.Button(frame_exportar_directo, text="Exportar a Excel", command=self.exportar_excel_flota,
                                   bg="#1E8449", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_excel.pack(side=tk.LEFT, expand=True, padx=5, fill=tk.X)

        self.btn_pdf = tk.Button(frame_exportar_directo, text="Exportar a PDF", command=self.exportar_pdf_flota,
                                 bg="#2471A3", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_pdf.pack(side=tk.LEFT, expand=True, padx=5, fill=tk.X)

        # Visualizacion de la tabla en el lado derecho.
        self.lf_tabla = tk.LabelFrame(self.contenedor, text=" Matriz de Asignaciones Activas ", padx=10, pady=10,
                                      font=("Arial", 10, "bold"))
        self.lf_tabla.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)
        # aqui creamos el espacio para que la union con el mouse suceda
        self.listbox_flota = tk.Listbox(self.lf_tabla, font=("Courier", 9), selectmode=tk.SINGLE)
        self.listbox_flota.pack(expand=True, fill="both", pady=5)


    # Procesamiento de datos
    def ejecutar_vinculacion_flota(self):
        # Validamos la entrada de datos, extraemos los datos los datos digitados por el usuario y lo limpiamos
        # Quitamos puntos o espacios con el .strip
        id_vehiculo = self.ent_vehiculo.get().strip()
        id_conductor = self.ent_conductor.get().strip()

        # aqui es donde validamos que no hayan campos vacios
        if not id_vehiculo or not id_conductor:
            messagebox.showerror("Campos Vacíos",
                                 "Error: Los campos ID Vehículo / ID Conductor son obligatorios.")
            return

        # validamos entrada numerica por medio de .isdigit
        if not id_vehiculo.isdigit() or not id_conductor.isdigit():
            messagebox.showerror("Error",
                                 "Error, los id vehiculo/conductor deben ser numericos.")
            return

        # Confirmacion antes de vincular al vehiculo con el conductor
        messagebox.showwarning(
            "LogiTrans - Flota",
            "El sistema procederá a verificar que el camión y el conductor estén en estado 'Disponible' antes del despacho."
        )

        # Aqui nos integramos con la db
        if self.db:
            # llamamos al procedimiento almacenado para actualizar la vinculación
            exito, mensaje = self.db.sp_asignar_conductor_vehiculo(int(id_conductor), int(id_vehiculo))
            if exito:
                # si es exitoso enviamos la info
                messagebox.showinfo("Operacion finalizada de form exitosa", mensaje)
                self.ent_vehiculo.delete(0, tk.END) # limpiamos los campos
                self.ent_conductor.delete(0, tk.END)
                self.cargar_tabla_visual()
            else:
                messagebox.showerror("Error Logístico", mensaje)

    def cargar_tabla_visual(self):
        # Limpiamos el tablero antes de hacer el read
        self.listbox_flota.delete(0, tk.END)


        if self.db:
            registros = self.db.sp_obtener_monitoreo_flota() # Obtenemos el procedimiento almacenado
            # y obtenemos el resultado de la flota
            if registros: # Recorremos cada registro
                for r in registros:
                    # Aqui damos la orden de como queremos que se vea el texto en la lista
                    self.listbox_flota.insert(tk.END, f"Asignación #{r} | Conductor: {r} | Placa: {r}")
            else:
                self.listbox_flota.insert(tk.END, "[No hay asignaciones registradas en la flota]")


    # Aqui vamos a crear la exportacion para la cual ya le hicimos el espacio
    def exportar_excel_flota(self):
        # inicializamos una hoja nueva y la activamos
        wb = Workbook()
        ws = wb.active
        ws.title = "Flota Asignaciones"
        ws.append(["Historial del Panel de Control de Flota"])

        # filtramos el vehiculo ingresado
        filtro_vehiculo = self.ent_vehiculo.get().strip()

        # iteramos registro por registro
        for i in range(self.listbox_flota.size()):
            linea = self.listbox_flota.get(i) # mostramos datos uno a uno
            if not filtro_vehiculo or filtro_vehiculo in linea:
                ws.append([linea]) # si pasa el filtro, se agrega la fila al Excel

        # Aqui le damos la ruta al archivo
        ruta_archivo = "Reporte_Flota_Modulo.xlsx"
        wb.save(ruta_archivo) # Guardamos
        # Enviamos mensaje info para decirle al usuario que se genero con exito
        messagebox.showinfo("Realizado",
                            f"¡Reporte Excel de flota generado correctamente!\nArchivo: {ruta_archivo}")

    # Aqui exportamos el pdf
    def exportar_pdf_flota(self):
        # Inicializamos pdf en blanco
        ruta_pdf = "Reporte_Flota_Modulo.pdf"
        c = canvas.Canvas(ruta_pdf, pagesize=letter)

        # Damos los parametros de config para el pdf que se va a generar
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "LOGITRANS - CONTROL DE RECURSOS Y OPERACIONES DE FLOTA")
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 735, f"Reporte de Monitoreo flota  |  Auditoría: Jenny Florez")
        c.line(50, 725, 550, 725) # linea que separa el encabezado
        y = 695 # Aqui damos la coordenada de ubicacion de los datos en el pdf
        c.setFont("Helvetica", 10)

        # Aqui añadimos los datos extraidos al pdf
        filtro_vehiculo = self.ent_vehiculo.get().strip() # limpiamos espacios, llamamos la funcion
        for i in range(self.listbox_flota.size()):
            linea = self.listbox_flota.get(i) # mostramos los datos uno a uno
            if not filtro_vehiculo or filtro_vehiculo in linea:
                c.drawString(50, y, linea)
                y -= 20 # Aqui evitamos que los datos se junten
                if y < 50:
                    c.showPage() #  Creamos una nueva pagina en blanco si los datos no caben en la primera
                    y = 700 # Reiniciamos el renglon de arriba de toda la nueva hoja
        # Guardamos pdf
        c.save()
        messagebox.showinfo("Realizado", f"¡Reporte PDF generado con éxito!\nArchivo: {ruta_pdf}")


if __name__ == '__main__':
    print("pruebas")
    root = tk.Tk()
    root.title("Módulo Flota")
    root.geometry("950x600")

    if os.path.exists("imagenes/logitrans_ico.ico"):
        root.iconbitmap("imagenes/logitrans_ico.ico")

    contenedor_prueba = tk.Frame(root)
    contenedor_prueba.pack(fill="both", expand=True)

    app_test = ModuloFlota(contenedor_prueba, conexion_db=None)

    root.mainloop()
