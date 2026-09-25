# Importamos modulos
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random
import os

# Creacion de la clase ModuloEnvios
class ModuloEnvios:

    # Inicializamos variables, creamos contenedor
    def __init__(self, contenedor, conexion_db):
        self.contenedor = contenedor
        self.db = conexion_db
        self.ruta_foto_guia = "imagenes/camion_logitrans.png"  # Imagen de la carpeta de imagenes
        self.inicializar_componentes()
        self.cargar_tabla_visual()

    def inicializar_componentes(self):
        # Formulario izquierdo
        self.lf_envio = tk.LabelFrame(self.contenedor, text=" Datos para generar la Guía de Distribución ", padx=15,
                                      pady=15, font=("Arial", 10, "bold"))
        self.lf_envio.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)

        # Implementacion de tkcalendar, entregamos la fecha exactamente como esta estipulada segun date_pattern
        tk.Label(self.lf_envio, text="Fecha Recepción:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_fecha = DateEntry(self.lf_envio, width=19, background='darkblue', foreground='white', borderwidth=2,
                                   date_pattern='yyyy-mm-dd')
        self.ent_fecha.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_envio, text="ID Cliente (Número):").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_id_cliente = tk.Entry(self.lf_envio, width=15)
        self.ent_id_cliente.grid(row=1, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_envio, text="Remitente:").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_remitente = tk.Entry(self.lf_envio, width=25)
        self.ent_remitente.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_envio, text="Destinatario:").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_destinatario = tk.Entry(self.lf_envio, width=25)
        self.ent_destinatario.grid(row=3, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_envio, text="Dirección Origen:").grid(row=4, column=0, sticky="w", pady=5)
        self.ent_origen = tk.Entry(self.lf_envio, width=30)
        self.ent_origen.grid(row=4, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_envio, text="Dirección Destino:").grid(row=5, column=0, sticky="w", pady=5)
        self.ent_destino = tk.Entry(self.lf_envio, width=30)
        self.ent_destino.grid(row=5, column=1, pady=5, padx=5, sticky="w")
        # Lista despleglable
        tk.Label(self.lf_envio, text="Tipo Servicio:").grid(row=6, column=0, sticky="w", pady=5)
        self.cmb_servicio = ttk.Combobox(self.lf_envio, values=["normal", "express", "mismo dia"], width=19,
                                         state="readonly")
        # Hace que la primera opción de incidente aparezca seleccionada por defecto al abrir el formulario
        self.cmb_servicio.current(0)
        self.cmb_servicio.grid(row=6, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_envio, text="Peso Declarado (Kg):").grid(row=7, column=0, sticky="w", pady=5)
        self.ent_peso = tk.Entry(self.lf_envio, width=15)
        self.ent_peso.grid(row=7, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_envio, text="Dimensiones (Alto x Ancho):").grid(row=8, column=0, sticky="w", pady=5)
        self.ent_dimensiones = tk.Entry(self.lf_envio, width=22)
        self.ent_dimensiones.grid(row=8, column=1, pady=5, padx=5, sticky="w")

        # Valor estimado del producto segun cliente
        tk.Label(self.lf_envio, text="Valor Estimado ($):").grid(row=9, column=0, sticky="w", pady=5)
        self.ent_costo = tk.Entry(self.lf_envio, width=15)
        self.ent_costo.grid(row=9, column=1, pady=5, padx=5, sticky="w")

        # Forma de pago
        tk.Label(self.lf_envio, text="Forma de pago:"). grid(row=10, column=0, sticky="w", pady=5)
        self.cmb_pago = ttk.Combobox(self.lf_envio, values=["Efectivo", "Tarjeta", "Transferencia"],
                                     width=19,state="readonly")
        self.cmb_pago.current(0)
        self.cmb_pago.grid(row=10, column=1, pady=5, padx=5, sticky="w")

        # Instrucciones NO obligatorias
        tk.Label(self.lf_envio, text="Instrucciones especiales").grid(row=11, column=0, sticky="w", pady=5)
        self.ent_instrucciones = tk.Entry(self.lf_envio,width=22)
        self.ent_instrucciones.grid(row=11, column=1, pady=5, padx=5, sticky="w")

        # Creacion del frame donde ira la imagen
        self.frame_guia_img = tk.Frame(self.lf_envio, width=110, height=90, relief="groove", borderwidth=2)
        self.frame_guia_img.grid(row=0, column=2, rowspan=4, padx=15, pady=5)
        self.frame_guia_img.pack_propagate(False)

        # Etiqueta interna donde ponemos que ocupe todo el espacio
        self.lbl_foto_guia = tk.Label(self.frame_guia_img)
        self.lbl_foto_guia.pack(fill="both", expand=True)
        self.cargar_miniatura_pillow(self.ruta_foto_guia)

        # Creacion de boton para cargar imagen
        self.btn_cargar_img = tk.Button(self.lf_envio, text="Cargar Foto", command=self.buscar_imagen_disco,
                                        font=("Arial", 9, "bold"), bg="#95A5A6")
        self.btn_cargar_img.grid(row=4, column=2, padx=15, sticky="ew")

        # Creacion de boton para guardar guia
        self.btn_guardar_guia = tk.Button(
            self.lf_envio,
            text="Generar Guía de Envío",
            command=self.registrar_orden_despacho,
            bg="#27AE60",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.btn_guardar_guia.grid(row=12, column=0, columnspan=3, pady=15, sticky="ew")

        # Creacion de botones de exportacion
        frame_exportar_directo = tk.Frame(self.lf_envio, pady=5)
        frame_exportar_directo.grid(row=13, column=0, columnspan=3, sticky="ew")

        self.btn_excel = tk.Button(frame_exportar_directo, text="Exportar a Excel", command=self.compilar_reporte_excel, bg="#1E8449", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_excel.pack(side=tk.LEFT, expand=True, padx=5, fill=tk.X)

        self.btn_pdf = tk.Button(frame_exportar_directo, text="Exportar a PDF", command=self.compilar_reporte_pdf, bg="#2471A3", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_pdf.pack(side=tk.LEFT, expand=True, padx=5, fill=tk.X)

        # Frame derecho
        self.lf_tabla = tk.LabelFrame(self.contenedor, text=" Envíos Activos en Sistema ", padx=10, pady=10, font=("Arial", 10, "bold"))
        self.lf_tabla.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)
        # aqui creamos el espacio para que la union con el mouse suceda
        self.listbox_envios = tk.Listbox(self.lf_tabla, font=("Courier", 9), selectmode=tk.SINGLE)
        self.listbox_envios.pack(expand=True, fill="both", pady=5)

    def buscar_imagen_disco(self):
        # Validacion de archivos de imagenes permitidas
        tipos = [("Imagenes de control", "*.png *.jpg *.jpeg *.gif")]
        ruta = filedialog.askopenfilename(filetypes=tipos)
        if ruta: # si son los formatos permitidos cargar
            self.ruta_foto_guia = ruta
            self.cargar_miniatura_pillow(ruta)

    def cargar_miniatura_pillow(self, ruta_img):
        # Si la ruta existe cargar imagen en archivo
        if os.path.exists(ruta_img):
            img = Image.open(ruta_img)
            img = img.resize((105, 85), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.BICUBIC)
            img_tk = ImageTk.PhotoImage(img)
            self.lbl_foto_guia.config(image=img_tk)
            self.lbl_foto_guia.image = img_tk

    def registrar_orden_despacho(self):
        guia_automatica = f"G-{random.randint(10000, 99999)}" # randint para generar guia automatica
        try: #extraemos el peso de la caja de texto y lo convertimos en un numero decimal
            peso_kg = float(self.ent_peso.get().strip() or 0.0)
        except ValueError:
            messagebox.showerror("Error", "El peso debe ser un número válido.")
            return

        # Jalamos el texto de las dimensiones, limpiamos espacios y pasamos a minisculas
        dim_texto = self.ent_dimensiones.get().strip().lower()
        # Creamos un interruptor apagado para controlar si el paquete requiere un cobro extra por tamaño
        recargo_dimension = False

        if 'x' in dim_texto:
            try:
                # Si encontramos la X, cortamos las dimensiones por el separador para sacar los tamaños
                partes = dim_texto.split('x')
                alto = float(partes[0].strip())
                ancho = float(partes[1].strip())
                # Si el alto o el ancho superan los 50 centímetros, encendemos el cobro extra
                if alto > 50 or ancho > 50:
                    recargo_dimension = True
            except (ValueError, IndexError):
                # para que pase sin problema sin generar error y cerrar de forma abrupta el programa
                pass

        tarifa_por_kg = 4000
        if recargo_dimension:
            tarifa_por_kg += 500
        # Aqui generamos el calculo del costo que aparecera en el mensaje de confirmacion de envio
        costo_final_calculado = peso_kg * tarifa_por_kg

        # Traemos los datos necesario de la db y generamos de forma automatica algunos para que no vaya a generar error

        datos = {
            'numero_guia': guia_automatica,
            'fecha_hora_recepcion': self.ent_fecha.get() + " 17:41:00",
            'id_cliente': self.ent_id_cliente.get().strip(),
            'remitente': self.ent_remitente.get().strip(),
            'destinatario': self.ent_destinatario.get().strip(),
            'direccion_origen': self.ent_origen.get().strip(),
            'direccion_destino': self.ent_destino.get().strip(),
            'tipo_servicio': self.cmb_servicio.get(),
            'descripcion_contenido': "Mercancía General Despachada",
            'peso': peso_kg,
            'dimensiones': self.ent_dimensiones.get().strip() or "N/A",
            'valor_declarado': self.ent_costo.get().strip() or "0.0",
            'costo': costo_final_calculado,
            'forma_pago': self.cmb_pago.get(),
            'estado_actual': "en transito",
            'instrucciones_especiales': self.ent_instrucciones.get().strip(),
            'ruta_distribucion': 1
        }

        # Validaciones de entrada de datos
        if not datos['id_cliente'] or not datos['direccion_destino']:
            messagebox.showerror("Error", "Los campos ID del Cliente y la Dirección Destino son obligatorios.")
            return

        # si el id cliente no es numerico lanza error
        if not str(datos['id_cliente']).isdigit():
            messagebox.showerror("Error", "El ID de Cliente debe ser un valor numérico.")
            return

        if self.db:
            exito, mensaje = self.db.sp_insertar_envio(datos) # traemos procedimiento almacenado y damos datos
            if exito:
                detalle_cobro = f"\n\n-GUIA\nTarifa por Kg: ${tarifa_por_kg:,}\nCOSTO TOTAL: ${costo_final_calculado:,}"
                messagebox.showinfo("Envio", f"{mensaje}\nNúmero de Guía asignado: {guia_automatica}{detalle_cobro}")
                self.limpiar_cajas()
                self.cargar_tabla_visual()
            else:
                messagebox.showerror("Falla Operativa", mensaje)
    # Cargar tabla visual
    def cargar_tabla_visual(self):
        # Extraemos los datos de mysql
        self.listbox_envios.delete(0, tk.END) # Limpiamos campos

        if self.db:
            registros = self.db.sp_obtener_todos_envios()
            if registros:
                for r in registros:
                    self.listbox_envios.insert(tk.END,
                                               f"Guía: {r[1]} | Cliente ID: {r[2]} | Destinatario: {r[3]} | Estado: {r[6]}")
            else:
                self.listbox_envios.insert(tk.END, "[No hay guías de envío registradas]")

    def compilar_reporte_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Envíos"
        ws.append(["Historial de Envíos en Sistema"])

        filtro_servicio = self.cmb_servicio.get()
        for i in range(self.listbox_envios.size()):
            linea = self.listbox_envios.get(i)
            if filtro_servicio in linea.lower() or filtro_servicio == "normal":
                ws.append([linea])

        ruta_archivo = f"Reporte_Envios_{filtro_servicio}.xlsx"
        wb.save(ruta_archivo)
        messagebox.showinfo("Realizado", f"¡Excel generado con éxito!\nArchivo: {ruta_archivo}")

    def compilar_reporte_pdf(self):
        filtro_servicio = self.cmb_servicio.get()
        ruta_pdf = f"Reporte_Envios_{filtro_servicio}.pdf"
        c = canvas.Canvas(ruta_pdf, pagesize=letter)

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "LOGITRANS - REPORTE DE AUDITORÍA DE ENVÍOS")
        c.line(50, 725, 550, 725)
        y = 695
        c.setFont("Helvetica", 10)
        for i in range(self.listbox_envios.size()):
            linea = self.listbox_envios.get(i)
            c.drawString(50, y, linea)
            y -= 20
        c.save()
        messagebox.showinfo("Realizado", f"¡PDF generado con exito!\nArchivo: {ruta_pdf}")

    # Funcion para limpiar campos
    def limpiar_cajas(self):
        self.ent_id_cliente.delete(0, tk.END)
        self.ent_remitente.delete(0, tk.END)
        self.ent_destinatario.delete(0, tk.END)
        self.ent_origen.delete(0, tk.END)
        self.ent_destino.delete(0, tk.END)
        self.ent_peso.delete(0, tk.END)
        self.ent_dimensiones.delete(0, tk.END)
        self.ent_costo.delete(0, tk.END)
        self.ruta_foto_guia = "camion_logitrans.png"
        self.cargar_miniatura_pillow(self.ruta_foto_guia)


if __name__ == '__main__':
    print("Pruebas")
    root = tk.Tk()
    root.title("Módulo Envíos")
    root.geometry("950x600")
    if os.path.exists("imagenes/logitrans_ico.ico"):
        root.iconbitmap("imagenes/logitrans_ico.ico")
    contenedor_prueba = tk.Frame(root)
    contenedor_prueba.pack(fill="both", expand=True)
    app_test = ModuloEnvios(contenedor_prueba, conexion_db=None)
    root.mainloop()


