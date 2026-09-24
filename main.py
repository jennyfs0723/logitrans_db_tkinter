# Importamos modulos
import tkinter as tk
from tkinter import ttk
import os
from conexion import ConexionLOGITRANS
from modulo_cliente import ModuloCliente
from modulo_envios import ModuloEnvios
from modulo_flota import ModuloFlota
from modulo_incidentes import ModuloIncidentes
from datetime import datetime

# Creamos la clase que nos va a mostrar en el encabezado los datos de ingreso
class ConfigSistema:
    VERSION = "v2.0"
    FECHA = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Hora y fecha real
    CLIENTE = "Jenny Florez"
    EMPRESA = "Logitrans"

    # Creamos la funcion que llama el encabezado, es un metodo de clase porque es llamado por cofigsistema
    @classmethod
    def obtener_encabezado(cls):
        return f"Cliente: {cls.CLIENTE}  |  Versión: {cls.VERSION}  |  Fecha: {cls.FECHA}  |  Empresa: {cls.EMPRESA}"

# Cremamos la clase aplicacion
class ApplicationLOGITRANS:
    def __init__(self, root):
        # Enviamos variables para inicializar la ventana
        self.root = root
        self.conexion_db = ConexionLOGITRANS()
        self.tema_oscuro = False # Aqui comenzamos con los parametros para cambiar de tema si lo deseamos
        self.configurar_ventana()
        self.inicializar_componentes()
        self.aplicar_estilos_globales()

# Configuracion de ventana
    def configurar_ventana(self):
        self.root.title("LOGITRANS - Sistema operativo")
        self.root.geometry("1000x650")
        # Aqui subimos la imagen .ico de la carpeta imegenes del proyecto
        if os.path.exists("imagenes/logitrans_ico.ico"):
            self.root.iconbitmap("imagenes/logitrans_ico.ico")

    # Inicializamos componentes
    def inicializar_componentes(self):
        self.frame_top = tk.Frame(self.root, pady=6, relief="groove", borderwidth=1)
        self.frame_top.pack(side=tk.TOP, fill=tk.X)

        self.lbl_meta = tk.Label(self.frame_top, text=ConfigSistema.obtener_encabezado(), font=("Arial", 9, "bold"),
                                 padx=10)
        self.lbl_meta.pack(side=tk.LEFT)

        # Creacion del boton para cambiar de color la ventana
        self.btn_tema = tk.Button(self.frame_top, text="Cambiar Tema", command=self.alternar_tema_visual,
                                  font=("Arial", 9, "bold"), relief="groove", padx=8)
        self.btn_tema.pack(side=tk.RIGHT, padx=10)

        # Creamos el sistema de pestañas superiores y hacemos que se estire al tamaño de la ventana
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Creamos las pestañas que iran en el sistema de pestañas
        self.pestana_cliente = ttk.Frame(self.notebook)
        self.pestana_envios = ttk.Frame(self.notebook)
        self.pestana_flota = ttk.Frame(self.notebook)
        self.pestana_incidentes = ttk.Frame(self.notebook)

        # Insertamos los datos a cada pestaña
        self.notebook.add(self.pestana_cliente, text="Registro de Clientes")
        self.notebook.add(self.pestana_envios, text="Registro de Envíos")
        self.notebook.add(self.pestana_flota, text="Control de Flota")
        self.notebook.add(self.pestana_incidentes, text="Reporte de Incidentes")

        # aqui es donde conectamos los datos insertados en las pestañas con los modulos creados anteriormente
        # y los conectamos a la db
        self.modulo_cliente_gui = ModuloCliente(self.pestana_cliente, self.conexion_db)
        self.modulo_envios_gui = ModuloEnvios(self.pestana_envios, self.conexion_db)
        self.modulo_flota_gui = ModuloFlota(self.pestana_flota, self.conexion_db)
        self.modulo_incidentes_gui = ModuloIncidentes(self.pestana_incidentes, self.conexion_db)
        # Amarramos el evento del mouse para que cuando cambie de pestaña,
        # el sistema refresque las tablas en tiempo real
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    # Según la pestaña activa, revisamos que el módulo exista y refrescamos su tabla en tiempo real
    def on_tab_changed(self, event):
        pestana_activa = self.notebook.index(self.notebook.select())
        if pestana_activa == 1:
            if hasattr(self, 'modulo_envios_gui'):
                self.modulo_envios_gui.cargar_tabla_visual()
        elif pestana_activa == 0:
            if hasattr(self, 'modulo_cliente_gui'):
                self.modulo_cliente_gui.cargar_tabla_visual()
        elif pestana_activa == 2:
            if hasattr(self, 'modulo_flota_gui'):
                self.modulo_flota_gui.cargar_tabla_visual()
        elif pestana_activa == 3:
            if hasattr(self, 'modulo_incidentes_gui'):
                self.modulo_incidentes_gui.cargar_tabla_visual()

    # cambiar color de ventana
    def alternar_tema_visual(self):
        self.tema_oscuro = not self.tema_oscuro
        self.aplicar_estilos_globales()
    # Aqui damos las dos opciones de estilos que iran cuando presionemos el boton creado
    def aplicar_estilos_globales(self):
        if self.tema_oscuro:
            bg_raiz = "#1E272C"
            bg_paneles = "#2C3E50"
            fg_texto = "#ECF0F1"
            estilo_nb = "clam"
        else:
            bg_raiz = "#EAECEE"
            bg_paneles = "#FFFFFF"
            fg_texto = "#2C3E50"
            estilo_nb = "default"

        # Aquí es donde ejecutamos el cambio de color real y pintamos cada pieza de la ventana con los tonos elegidos
        self.root.config(bg=bg_raiz)
        self.frame_top.config(bg=bg_paneles)
        self.lbl_meta.config(bg=bg_paneles, fg=fg_texto) # Cambiamos fondo y color de letra para que resalte
        self.btn_tema.config(bg=bg_raiz, fg=fg_texto, activebackground=bg_paneles, activeforeground=fg_texto)

        # Activamos el motor de estilos para poder pintar las pestañas superiores y darles un diseño acolchado
        estilo = ttk.Style()
        estilo.theme_use(estilo_nb)
        estilo.configure("TNotebook", background=bg_raiz)
        estilo.configure("TNotebook.Tab", font=("Arial", 9, "bold"), padding=[10, 5])
        #Letra en negrita y botones más grandes

# Inicializacion de sistema
if __name__ == '__main__':
    root = tk.Tk()
    app = ApplicationLOGITRANS(root)
    root.mainloop()
