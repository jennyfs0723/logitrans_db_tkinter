# importamos modulos
import tkinter as tk
from tkinter import ttk, messagebox
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random
import os
from datetime import datetime


# Creacion clase ModuloIncidentes
class ModuloIncidentes:
    # Inicializamos variables, creamos contenedor
    def __init__(self, contenedor, conexion_db):
        self.contenedor = contenedor
        self.db = conexion_db
        self.inicializar_componentes()
        self.cargar_tabla_visual()

    def inicializar_componentes(self):
        # Aqui creamos el marco izquierdo de la ventana
        self.lf_incidentes = tk.LabelFrame(self.contenedor, text=" Reporte de Novedades e Incidentes en Ruta ", padx=15,
                                           pady=15, font=("Arial", 10, "bold"))
        self.lf_incidentes.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)

        # Campos organizados con .grid() y damos entrada de escritura
        tk.Label(self.lf_incidentes, text="ID Vehículo Afectado (Número):").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_vehiculo_id = tk.Entry(self.lf_incidentes, width=15)
        self.ent_vehiculo_id.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_incidentes, text="ID Conductor (Número):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_conductor_id = tk.Entry(self.lf_incidentes, width=15)
        self.ent_conductor_id.grid(row=1, column=1, pady=5, padx=5, sticky="w")

        # Aqui es donde ponemos selecciones multiples
        tk.Label(self.lf_incidentes, text="Tipo de Incidente:").grid(row=2, column=0, sticky="w", pady=5)
        self.cmb_tipo_incidente = ttk.Combobox(self.lf_incidentes,
                                               values=["Falla Mecánica", "Pinchazo", "Accidente Vial",
                                                       "Retraso", "Condición Climática", "Otro"], width=22,
                                               state="readonly")
        # Hace que la primera opción de incidente aparezca seleccionada por defecto al abrir el formulario
        self.cmb_tipo_incidente.current(0)
        self.cmb_tipo_incidente.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_incidentes, text="Ubicación (Direccion/Ciudad):").grid(row=3, column=0, sticky="w",
                                                                                        pady=5)
        self.ent_ubicacion = tk.Entry(self.lf_incidentes, width=30)
        self.ent_ubicacion.grid(row=3, column=1, pady=5, padx=5, sticky="w")


        tk.Label(self.lf_incidentes, text="Descripción Detallada:").grid(row=4, column=0, sticky="w", pady=5)
        self.txt_descripcion = tk.Entry(self.lf_incidentes, width=40)
        self.txt_descripcion.grid(row=4, column=1, pady=5, padx=5, sticky="w")

        # Boton de alerta
        self.btn_emitir_alerta = tk.Button(
            self.lf_incidentes,
            text="Emitir reporte de incidente",
            command=self.ejecutar_reporte_incidente,
            bg="#C0392B",
            fg="white",
            font=("Arial", 10, "bold")
        )
        # Publicacion del boton
        self.btn_emitir_alerta.grid(row=5, column=0, columnspan=2, pady=15, sticky="ew")

        # Creacion de botones de exportacion pdf y excel
        frame_exportar_directo = tk.Frame(self.lf_incidentes, pady=5)
        frame_exportar_directo.grid(row=6, column=0, columnspan=2, sticky="ew")

        self.btn_excel = tk.Button(frame_exportar_directo, text="Exportar a Excel",
                                   command=self.exportar_excel_incidentes, bg="#1E8449", fg="white",
                                   font=("Arial", 10, "bold"), width=15)
        self.btn_excel.pack(side=tk.LEFT, expand=True, padx=5, fill=tk.X)

        self.btn_pdf = tk.Button(frame_exportar_directo, text="Exportar a PDF", command=self.exportar_pdf_incidentes,
                                 bg="#2471A3", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_pdf.pack(side=tk.LEFT, expand=True, padx=5, fill=tk.X)

        # Creacion de panel derecho
        self.lf_tabla = tk.LabelFrame(self.contenedor, text=" Registro Histórico de Incidentes ", padx=10, pady=10,
                                      font=("Arial", 10, "bold"))
        self.lf_tabla.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)
        # aqui creamos el espacio para que la union con el mouse suceda
        self.listbox_incidentes = tk.Listbox(self.lf_tabla, font=("Courier", 9), selectmode=tk.SINGLE)
        self.listbox_incidentes.pack(expand=True, fill="both", pady=5)

    # Procesamiento de datos
    def ejecutar_reporte_incidente(self):
        # Create de alertas, limpiamos espacios.
        v_id = self.ent_vehiculo_id.get().strip()
        c_id = self.ent_conductor_id.get().strip()
        ubicacion = self.ent_ubicacion.get().strip()
        desc = self.txt_descripcion.get().strip() # Aqui ajustamos si la descripcion es larga

        # Validaciones, si no hay datos ingresados no se pueden generar reportes
        if not v_id or not c_id or not ubicacion or not desc:
            messagebox.showerror("Campos Incompletos",
                                 "Error: Todos los campos del reporte de incidente son obligatorios.")
            return

        # Validacion numerica con .isdigit --> Rechaza letras
        if not v_id.isdigit() or not c_id.isdigit():
            messagebox.showerror("Error",
                                 "Los códigos de vehículo y conductor deben contener únicamente números.")
            return
        # Aqui por medio de randint vamos a generar el codigo aleatorio
        codigo_alerta = f"IS-{random.randint(10000, 99999)}"
        # Aqui vamos a dejar el incidente con la fecha ya hora exacta que se reporta
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Simulamos la ubicacion geografica
        gps_simulado = f"{random.uniform(6.1, 6.3):.4f}, -75.5888"

        # Aqui tenemos todo lo que la db necesita reunir, por este motivo hay unos datos inventados.
        datos = {
            'vehiculo_id': int(v_id),
            'conductor_id': int(c_id),
            'codigo': codigo_alerta,
            'fecha_hora': fecha_actual,
            'tipo_incidente': self.cmb_tipo_incidente.get(),
            'ubicacion': ubicacion,
            'descripcion': desc,
            'causas': "Investigación en curso", # Inventado
            'consecuencias': "Retraso logístico controlado", # Inventado
            'medidas_tomadas': "Asistencia enviada por centro de control", # Inventado
            'estado_resolucion': "Pendiente" # Inventado
        }

        # Alerta de incidente registrado
        messagebox.showerror(
            "LOGITRANS",
            f"¡Incidente Reportado!\nSe ha notificado al Centro de Distribución de forma prioritaria."
            f"\n\nCódigo: {codigo_alerta}\nUbicación GPS Enviada: {gps_simulado}"
        )

        if self.db:
            exito, mensaje = self.db.sp_insertar_incidente(datos) # Aqui traemos el procedimiento almacenado
            if exito:
                self.limpiar_campos() # Limpiamos campos
                self.cargar_tabla_visual() # Recargamos tabla
            else:
                messagebox.showerror("Error de Red", mensaje)


    def cargar_tabla_visual(self):
        # Limpiamos el tablero antes de hacer el read
        self.listbox_incidentes.delete(0, tk.END)

        if self.db:
            registros = self.db.sp_obtener_incidentes_activos() # Obtenemos el procedimiento almacenado
            if registros:
                for r in registros:
                    # Aqui damos la orden de como queremos que se vea el texto en la lista
                    self.listbox_incidentes.insert(tk.END, f"Alerta {r} | Fecha: {r} | Placa: {r} | Tipo: {r}")
            else:
                self.listbox_incidentes.insert(tk.END, "[No hay incidentes viales activos en las rutas]")


    # Exportacion pdf y excel
    def exportar_excel_incidentes(self):
        # inicializamos la hoja en blanco
        wb = Workbook()
        ws = wb.active
        ws.title = "Incidentes"
        ws.append(["Historial de Control de Incidentes"])
        # Filtramos el incidente ingresado
        filtro_tipo = self.cmb_tipo_incidente.get()

        for i in range(self.listbox_incidentes.size()):
            linea = self.listbox_incidentes.get(i)
            ws.append([linea])
            # Aqui no es necesario hacerle validacion de campos, dado que tenemos una lista desplegable

        ruta_archivo = "Reporte_Incidentes_Modulo.xlsx"
        wb.save(ruta_archivo)
        messagebox.showinfo("openpyxl Realizado",
                            f"¡Excel de incidentes generado correctamente!\nArchivo: {ruta_archivo}")
    # Exportamos a pdf
    def exportar_pdf_incidentes(self):
        # Creamos la hoja y damos parametros
        filtro_tipo = self.cmb_tipo_incidente.get()
        ruta_pdf = "Reporte_Incidentes_Modulo.pdf"
        c = canvas.Canvas(ruta_pdf, pagesize=letter)

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "LOGITRANS - CONTROL DE RECURSOS Y OPERACIONES DE FLOTA")
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 735, f"Reporte de Contingencias y Siniestros  |  Filtro Automático: {filtro_tipo}")
        c.line(50, 725, 550, 725)
        y = 695
        c.setFont("Helvetica", 10)

        for i in range(self.listbox_incidentes.size()):
            linea = self.listbox_incidentes.get(i)
            c.drawString(50, y, linea)
            y -= 20
            if y < 50:
                c.showPage()
                y = 700

        c.save()
        messagebox.showinfo("Realizado",
                            f"¡Reporte de incidentes guardado con éxito!\nArchivo: {ruta_pdf}")
    # Funcion para limpiar campos
    def limpiar_campos(self):
        self.ent_vehiculo_id.delete(0, tk.END)
        self.ent_conductor_id.delete(0, tk.END)
        self.ent_ubicacion.delete(0, tk.END)
        self.txt_descripcion.delete(0, tk.END)
        self.cmb_tipo_incidente.current(0)



if __name__ == '__main__':
    print("pruebas")
    root = tk.Tk()
    root.title("Modulo Incidentes")
    root.geometry("950x600")

    if os.path.exists("imagenes/logitrans_ico.ico"):
        root.iconbitmap("imagenes/logitrans_ico.ico")

    contenedor_prueba = tk.Frame(root)
    contenedor_prueba.pack(fill="both", expand=True)

    app_test = ModuloIncidentes(contenedor_prueba, conexion_db=None)

    root.mainloop()
