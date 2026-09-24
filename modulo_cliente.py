# Importamos modulos
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random
import re
import os

# Creacion de la clase ModuloCliente
class ModuloCliente:
    # Vamos a diseñar el formulario visual
    def __init__(self, contenedor, conexion_db): # contenedor sera la pantalla donde vamos a poner los datos
        # la conexion es donde vamos a conectarnos con la db
        self.contenedor = contenedor
        self.db = conexion_db
        self.ruta_imagen_cargada = "imagenes/camion_logitrans.png"  # Imagen de la carpeta imagenes
        self.cliente_seleccionado_id = None  # Control interno para la operación de Update,
        # si no es None da un valor
        self.inicializar_componentes() # estamos creando las variables para iniciar rutas y cargar tabla
        self.cargar_tabla_visual()

    def inicializar_componentes(self): # aqui vamos a crear el contenedor de la tabla
        # Creamos el frame
        self.lf_formulario = tk.LabelFrame(self.contenedor, text=" Datos para Creación de Cliente ", padx=15, pady=15,
                                           font=("Arial", 10, "bold"))
        self.lf_formulario.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
        # aqui le decimos que se acomodara a la izquierda, y tendra un tamaño de 10

        # Configuración de los campos
        tk.Label(self.lf_formulario, text="Tipo Cliente:").grid(row=0, column=0, sticky="w", pady=5)
        # Aqui estamos creando un menu desplegable para que seleccione la opcion de tipo de cliente,
        # Facilita el proceso y lo hace mas amigable
        self.cmb_tipo = ttk.Combobox(self.lf_formulario, values=["individual", "empresarial"], width=19,
                                     state="readonly")
        # Aqui le estamos diciendo al sistema que muestre el valor 0 cuando el menu aun no esta desplegado
        self.cmb_tipo.current(0)
        # Aqui vamos a decirle al sistema donde queremos que aparezca el campo
        self.cmb_tipo.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        # label de formulario y entrada con texto para el usuario
        tk.Label(self.lf_formulario, text="Nombre / Empresa:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_nombre = tk.Entry(self.lf_formulario, width=30)
        self.ent_nombre.grid(row=1, column=1, pady=5, padx=5, sticky="w") # Creacion del margenes y posicion

        # Requerimiento, validacion de nit o cedula
        tk.Label(self.lf_formulario, text="Cc / Nit (Solo Números):").grid(row=2, column=0, sticky="w", pady=5)
        #Entrada de texto
        self.ent_rut = tk.Entry(self.lf_formulario, width=22)
        # Tamaño, columna, posicion
        self.ent_rut.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_formulario, text="Dirección Fiscal:").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_dir_fiscal = tk.Entry(self.lf_formulario, width=30)
        self.ent_dir_fiscal.grid(row=3, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_formulario, text="Teléfono:").grid(row=4, column=0, sticky="w", pady=5)
        self.ent_telefono = tk.Entry(self.lf_formulario, width=22)
        self.ent_telefono.grid(row=4, column=1, pady=5, padx=5, sticky="w")

        # Validacion de email con @ y .
        tk.Label(self.lf_formulario, text="Correo Electrónico:").grid(row=5, column=0, sticky="w", pady=5)
        self.ent_email = tk.Entry(self.lf_formulario, width=30)
        self.ent_email.grid(row=5, column=1, pady=5, padx=5, sticky="w")

        tk.Label(self.lf_formulario, text="Persona Contacto:").grid(row=6, column=0, sticky="w", pady=5)
        self.ent_contacto = tk.Entry(self.lf_formulario, width=30)
        self.ent_contacto.grid(row=6, column=1, pady=5, padx=5, sticky="w")

        # aqui entra la gestion de imagenes
        self.frame_foto = tk.Frame(self.lf_formulario, width=110, height=90, relief="groove", borderwidth=2)
        self.frame_foto.grid(row=0, column=2, rowspan=4, padx=15, pady=5)
        self.frame_foto.pack_propagate(False) # para que no se pueda propagar la imagen

        #Aquí metemos una etiqueta limpia dentro del recuadro de la foto, le decimos que se estire para ocupar
        # el espacio que esta disponible y llamamos a la funcion que dibuja la imagen
        self.lbl_foto = tk.Label(self.frame_foto)
        self.lbl_foto.pack(fill="both", expand=True) # para que se expanda por todo el recuadro
        self.actualizar_miniatura_foto(self.ruta_imagen_cargada) # aqui ponemos la imagen que cargamos en el __init__

        # aqui incluimos el boton para gestion de imagenes
        self.btn_cargar_foto = tk.Button(self.lf_formulario, text="📸 Cargar Foto",
                                         command=self.seleccionar_imagen_disco, font=("Arial", 9, "bold"), bg="#95A5A6")
        self.btn_cargar_foto.grid(row=4, column=2, padx=15, sticky="ew")

        # Botones de registrar y actualizar
        self.btn_guardar = tk.Button(
            self.lf_formulario, # llamamos al formulario
            text=" Registrar Cliente",
            command=self.ejecutar_guardado_cliente,
            bg="#27AE60",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.btn_guardar.grid(row=7, column=0, columnspan=2, pady=15, sticky="ew", padx=2)

        # Creacion de boton para actualizar cliente
        self.btn_actualizar = tk.Button(
            self.lf_formulario,
            text="Actualizar Cambios",
            command=self.ejecutar_actualizacion_cliente,
            bg="#D35400",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.btn_actualizar.grid(row=7, column=2, pady=15, sticky="ew", padx=2)

        #exportacion de pdf o excel
        frame_exportar_directo = tk.Frame(self.lf_formulario, pady=5) # llamamos al formulario
        frame_exportar_directo.grid(row=8, column=0, columnspan=3, sticky="ew") # ubicacion en ventana

        # boton exportacion excel
        self.btn_excel = tk.Button(frame_exportar_directo, text="Exportar a Excel",
                                   command=self.exportar_excel_clientes, bg="#1E8449", fg="white",
                                   font=("Arial", 10, "bold"), width=15)
        self.btn_excel.pack(side=tk.LEFT, expand=True, padx=5, fill=tk.X)

        # Boton de exportacion pdf
        self.btn_pdf = tk.Button(frame_exportar_directo, text="Exportar a PDF", command=self.exportar_pdf_clientes,
                                 bg="#2471A3", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_pdf.pack(side=tk.LEFT, expand=True, padx=5, fill=tk.X)

        # Visualizacion de datos, estara a la derecha de donde registramos clientes
        self.lf_tabla = tk.LabelFrame(self.contenedor, text=" Clientes en Base de Datos ", padx=10, pady=10,
                                      font=("Arial", 10, "bold"))
        self.lf_tabla.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)
        # Aqui creamos la lista de clientes, por medio de listbox los mostramos hacia abajo
        self.listbox_clientes = tk.Listbox(self.lf_tabla, font=("Courier", 9), selectmode=tk.SINGLE)
        self.listbox_clientes.pack(expand=True, fill="both", pady=5)
        # bind lo usamos para conectar el mouse con la funcion del codigo, en este caso tenemos opciones del CRUD
        self.listbox_clientes.bind("<<ListboxSelect>>", self.cargar_cliente_seleccionado_en_campos)
        # el listboxselect es para unir la seleccion del mouse con la data base

        # Boton para eliminar cliente
        self.btn_eliminar = tk.Button(
            self.lf_tabla,
            text="Eliminar Cliente Seleccionado",
            command=self.ejecutar_eliminacion_cliente, # llamamos al comando para eliminar
            bg="#C0392B",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.btn_eliminar.pack(fill=tk.X, pady=5)

    # Aqui definimos las acciones

    def seleccionar_imagen_disco(self):
        # Validacion de archivos de imagenes permitidas
        tipos_archivos = [("Imágenes de Control", "*.png *.jpg *.jpeg *.gif")]
        ruta = filedialog.askopenfilename(filetypes=tipos_archivos)
        if ruta: # si son los formatos permitidos cargar
            self.ruta_imagen_cargada = ruta
            self.actualizar_miniatura_foto(ruta)

    def actualizar_miniatura_foto(self, ruta_imagen):
        # Actualizar foto miniatura
        if os.path.exists(ruta_imagen): # si el archivo pertenece a la carpeta de ejecuta
            img = Image.open(ruta_imagen) # abrimos la imagen
            # Aqui le damos el tamaño a la imagen para que quepa en el recuadro que creamos para ella
            img = img.resize((105, 85), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.BICUBIC)
            # llamamos a la etiqueta
            img_tk = ImageTk.PhotoImage(img)
            # esta parte del codigo nos permite que python conserve la imagen y no la borre
            self.lbl_foto.config(image=img_tk)
            self.lbl_foto.image = img_tk

    # Aqui llamamos a la funcion para guardar cliente
    def ejecutar_guardado_cliente(self):
        # Generamos el codigo automatico por medio de randint le damos un rango numerico
        codigo_automatico = f"CL-{random.randint(1000, 9999)}"

        # llamamos a los datos del formulario
        datos = self.obtener_datos_formulario()
        datos['codigo_unico'] = codigo_automatico # Renombramos la funcion de codigo unico de la db para que sea
        # automatico en el sistema de creacion de cliente

        # validaciones
        # si no ha escrito los datos en el campo, no permitira guardar cliente
        if not datos['nombre_o_razon_social'] or not datos['rut_o_dni']:
            messagebox.showerror("Error de Campos", "Los campos Nombre/Empresa y Cc/Nit son obligatorios.")
            return

        # si los datos cc/nit no son numericos envia un mensaje de error
        if not datos['rut_o_dni'].isdigit():
            messagebox.showerror("Error Numérico",
                                 "El campo Cc / Nit solo permite numeros, intente de nuevo.")
            return

        # Validacion de email
        patron_correo = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        # Creamos los campos requeridos o validos
        # con re.match comprobamos si los campos cumplen con el requerimiento especifico, pasamos el re.match
        # y despues pasamos el requerimiento, en este caso datos
        if datos['email'] and not re.match(patron_correo, datos['email']):
            # mensaje de error solicitando que escriba bien el correo
            messagebox.showerror("Error", "El formato del correo electrónico ingresado no es válido "
                                 "(Ejemplo: usuario@dominio.com).")
            return

        # Envío a la base de datos el cliente si todas las validaciones se dan con exito
        if self.db: #llamamos la funcion conexion con la database creada en el __init__
            exito, mensaje = self.db.sp_insertar_cliente(datos) # insertamos los datos del cliente a la db
            if exito: # si es exitoso enviamos un mensaje confirmando
                messagebox.showinfo("Operación Exitosa","\nCliente registrado correctamente")

                # limpiamos la ventana
                self.limpiar_formulario()
                # recargamos la ventana
                self.cargar_tabla_visual()
            else: # si no enviamos un mensaje de error
                messagebox.showerror("Error en Base de Datos", mensaje)
    # actualizacion de cliente
    def ejecutar_actualizacion_cliente(self):

        # llamamos al procedimiento almacenado, si
        if not self.cliente_seleccionado_id:
            messagebox.showwarning("Error", "Por favor seleccione primero un cliente de la lista de la "
                                   "derecha para poder editarlo.")
            return
        # Obtenemos los datos del formulario
        datos = self.obtener_datos_formulario()
        # Actualizamos cliente por id
        datos['cliente_id'] = self.cliente_seleccionado_id

        # Mensaje para confirmar la actualizacion
        if messagebox.askyesno("Confirmar Actualización",
                               "¿Está segur@ de que desea guardar los cambios sobre este registro?"):
            if self.db:
                # llamamos los datos de mysql
                exito, mensaje = self.db.sp_actualizar_cliente(datos)
                if exito:
                    messagebox.showinfo("Registro actualizado", mensaje)
                    self.limpiar_formulario()
                    self.cargar_tabla_visual()
                else:
                    messagebox.showerror("Error Logístico", mensaje)
     # creamos la funcion para eliminar cliente
    def ejecutar_eliminacion_cliente(self):
        # curselection es para saber exactamente que estamos seleccionando desde el mouse
        seleccion = self.listbox_clientes.curselection()
        if not seleccion: # si no se selecciona solicitamos nuevamente que lo seleccione para poderlo eliminar
            messagebox.showwarning("Atención", "Por favor seleccione un cliente de la lista para proceder.")
            return
        # Mensaje de confirmacion
        confirmar = messagebox.askyesno(
            "Atencion",
            "¿Está completamente segur@ de que desea eliminar este cliente de la base de datos?"
            "\nEsta acción no se puede deshacer."
        )

        # si confirma
        if confirmar:
            if self.db:
                texto_fila = self.listbox_clientes.get(seleccion) # Traemos la seleccion de cliente
                # Envolvemos el proceso en un try - except
                try:
                    # como estamos guardando los clientes en fila, este comando sirve
                    # que extraiga solo el id a eliminar
                    cliente_id = int(texto_fila.split(" | ")[0])

                    exito, mensaje = self.db.sp_eliminar_cliente(cliente_id)
                    if exito:
                        messagebox.showinfo("Éxito", mensaje)
                        self.limpiar_formulario()
                        self.cargar_tabla_visual()
                    else:
                        messagebox.showerror("Error al borrar", mensaje)
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"No se pudo extraer el ID del cliente: {e}")


    def cargar_cliente_seleccionado_en_campos(self, event):
        # Cargamos el cliente seleccionado en el mouse
        seleccion = self.listbox_clientes.curselection()
        if not seleccion:
            return

        texto_fila = self.listbox_clientes.get(seleccion) # Cargamos la seleccion a la ventana con los datos
        try:
            # separamos los elementos y los ubica en el espacio que van
            self.cliente_seleccionado_id = int(texto_fila.split(" | ")[0])
        except (ValueError, IndexError):
            return

        if self.db:
            conn = self.db.conectar() # llamamos al metodo para conectarnos a la data base
            # Aqui hacemos la operacion CRUD, la encapsulamos en el bloque try para evitar que el programa se
            #cierre de forma abrupta si algo sucede
            if conn:
                try:
                    cursor = conn.cursor() # inicializamos el cursor
                    cursor.execute(
                        "SELECT tipo_cliente, nombre_o_razon_social, rut_o_dni, direccion_fiscal, "
                        "telefono, email, persona_contacto FROM cliente WHERE clienteID = %s",
                        (self.cliente_seleccionado_id,)) # aqui va el crud
                    res = cursor.fetchone() # traemos los datos exacto de la database
                    if res:
                        # Si el cliente existe, limpiamos las cajas desde el inicio al fin y
                        # metemos los datos nuevos de la db
                        self.cmb_tipo.set(res[0])
                        self.ent_nombre.delete(0, tk.END)
                        self.ent_nombre.insert(0, res[1])
                        self.ent_rut.delete(0, tk.END)
                        self.ent_rut.insert(0, res[2])
                        self.ent_dir_fiscal.delete(0, tk.END)
                        self.ent_dir_fiscal.insert(0, res[3])
                        self.ent_telefono.delete(0, tk.END)
                        self.ent_telefono.insert(0, res[4])
                        self.ent_email.delete(0, tk.END)
                        self.ent_email.insert(0, res[5])
                        self.ent_contacto.delete(0, tk.END)
                        self.ent_contacto.insert(0, res[6])
                    cursor.close() # Cerramos intermediario
                    conn.close() # cerramos la conexion
                except Exception as e:
                    print(f"Error al leer cliente: {e}")

    def obtener_datos_formulario(self):
        # mapeo de los campos del formulario
        # Aqui le estamos diciendo a pycharm, oye en la db se llama de una forma, pero va en el lugar donde esta
        #Creado este frame: ...
        return {
            'tipo_cliente': self.cmb_tipo.get(),
            'nombre_o_razon_social': self.ent_nombre.get().strip(),
            'rut_o_dni': self.ent_rut.get().strip(),
            'direccion_fiscal': self.ent_dir_fiscal.get().strip(),
            'direccion_recogida': self.ent_dir_fiscal.get().strip(),
            'telefono': self.ent_telefono.get().strip(),
            'email': self.ent_email.get().strip(),
            'persona_contacto': self.ent_contacto.get().strip(),
            'termino_pago': "Contado",
            'clasificacion_por_envio': "estándar"
        }

    def cargar_tabla_visual(self):
        # Limpiamos el listbox por completo antes de leer (Read) los clientes en tiempo real
        self.listbox_clientes.delete(0, tk.END)

        if self.db:
            conn = self.db.conectar()
            if conn:
                try:
                    cursor = conn.cursor()
                    # Ejecutamos CRUD select para ver los clientes
                    cursor.execute(
                        "SELECT clienteID, nombre_o_razon_social, rut_o_dni FROM cliente ORDER BY clienteID DESC")
                    filas = cursor.fetchall()
                    for f in filas: # aqui recorremos cada cliente de la db
                        self.listbox_clientes.insert(tk.END, f"{f[0]} | {f[1]} | NIT: {f[2]}")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"Error al refrescar listbox: {e}")

    # Creamos la funcion para exportar
    def exportar_excel_clientes(self):
        wb = Workbook() # Funcion para crear un libro en excel
        ws = wb.active # Seleccionamos y activamos la primera hoja del libro
        ws.title = "Clientes"
        ws.append(["Clientes logitrans"])
        filtro_tipo = self.cmb_tipo.get()

        # Recorremos cada cliente de la lista para que los muestre
        for i in range(self.listbox_clientes.size()):
            linea = self.listbox_clientes.get(i) # en linea estamos obteniendo los clientes
            ws.append([linea]) # aqui los agregamos al excel

        ruta_archivo = f"Reporte_Clientes_{filtro_tipo}.xlsx" # Generamos el archivo
        wb.save(ruta_archivo) # Guardamos el archivo
        messagebox.showinfo("Realizado", f"¡Excel generado correctamente!\nArchivo: {ruta_archivo}")

    # Generar reporte pdf
    def exportar_pdf_clientes(self):
        filtro_tipo = self.cmb_tipo.get()
        ruta_pdf = f"Reporte_Clientes_{filtro_tipo}.pdf"
        c = canvas.Canvas(ruta_pdf, pagesize=letter) # Aqui cremoas el archivo pdf desde cero

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "Logitrans - Reporte de auditoria de clientes")
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 735, f"Filtro Automático de Cuenta: {filtro_tipo}  |  Auditoría: Jenny Florez")
        c.line(50, 725, 550, 725)

        y = 695
        c.setFont("Helvetica", 10)
        for i in range(self.listbox_clientes.size()):
            linea = self.listbox_clientes.get(i)
            c.drawString(50, y, linea)
            y -= 20
            if y < 50:
                c.showPage()
                y = 700
        c.save()
        messagebox.showinfo("Realizado", f"¡PDF generado con exito!\nArchivo: {ruta_pdf}")

    # Aqui limpiamos formulario
    def limpiar_formulario(self):
        # Reiniciamos el formulario por completo: borramos las cajas,
        # el ID seleccionado y regresamos la foto del camion
        self.cliente_seleccionado_id = None
        self.ent_nombre.delete(0, tk.END)
        self.ent_rut.delete(0, tk.END)
        self.ent_dir_fiscal.delete(0, tk.END)
        self.ent_telefono.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_contacto.delete(0, tk.END)
        self.cmb_tipo.current(0)
        self.ruta_imagen_cargada = "camion_logitrans.png"
        self.actualizar_miniatura_foto(self.ruta_imagen_cargada)

if __name__ == '__main__':
    print("Pruebas")
    root = tk.Tk()
    root.title("Módulo Clientes")
    root.geometry("950x600")

    if os.path.exists("imagenes/logitrans_ico.ico"): # Aqui es donde esta ubicado el archivo .ico
        root.iconbitmap("imagenes/logitrans_ico.ico")

    contenedor_prueba = tk.Frame(root)
    contenedor_prueba.pack(fill="both", expand=True)

    app_test = ModuloCliente(contenedor_prueba, conexion_db=None)

    root.mainloop()

