import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from controllers.ch_controller import CHController
from controllers.dh_controller import DHController

class MainView:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador DH CH")

        # Crear la carpeta de logs al iniciar la aplicación
        self.setup_logging()

        self.create_widgets()

    def setup_logging(self):
        # Definir la ruta de la carpeta de logs
        log_dir = "logs"

        # Crear la carpeta si no existe
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Directorio {log_dir} creado para almacenar los logs.")

        # Configurar el logging para escribir en la carpeta de logs
        logging.basicConfig(
            filename=os.path.join(log_dir, "app.log"),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        logging.info("Aplicación iniciada")

    def create_widgets(self):
        # Etiquetas y entradas de texto
        tk.Label(self.root, text="Ruta de lectura de archivos").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Ruta de datos generados").grid(row=1, column=0, padx=10, pady=10)

        self.input_dir = tk.Entry(self.root, width=40)
        self.input_dir.grid(row=0, column=1, padx=10, pady=10)

        self.output_dir = tk.Entry(self.root, width=40)
        self.output_dir.grid(row=1, column=1, padx=10, pady=10)

        # Botones para examinar carpetas
        tk.Button(self.root, text="Examinar", command=self.select_input_dir).grid(row=0, column=2, padx=10)
        tk.Button(self.root, text="Examinar", command=self.select_output_dir).grid(row=1, column=2, padx=10)

        # Etiqueta para seleccionar el formato
        tk.Label(self.root, text="Seleccionar formato de archivo:").grid(row=2, column=0, padx=10, pady=10)

        # Opción para seleccionar el formato (mseed o seg2)
        self.file_format = tk.StringVar(value="mseed")  # Valor por defecto es mseed
        tk.Radiobutton(self.root, text="MSEED", variable=self.file_format, value="mseed").grid(row=3, column=0, padx=10, pady=5)
        tk.Radiobutton(self.root, text="SEG2", variable=self.file_format, value="seg2").grid(row=3, column=1, padx=10, pady=5)

        # Botones para generar CH y DH
        tk.Button(self.root, text="Generar CH", command=self.generar_ch).grid(row=4, column=0, padx=10, pady=20)
        tk.Button(self.root, text="Generar DH", command=self.generar_dh).grid(row=4, column=2, padx=10, pady=20)

        # Label de estado
        self.status_label = tk.Label(self.root, text="", fg="red")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=10)

        # Label de "Desarrollado por Yafel"
        self.developer_label = tk.Label(self.root, text="Desarrollado por Yafel", fg="blue")
        self.developer_label.grid(row=4, column=0, columnspan=3, pady=5)

    def select_input_dir(self):
        self.input_dir.delete(0, tk.END)
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir.insert(0, directory)

    def select_output_dir(self):
        self.output_dir.delete(0, tk.END)
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.insert(0, directory)

    def generar_ch(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        selected_format = self.file_format.get()  # Obtener el formato seleccionado (mseed o seg2)

        if not input_dir or not output_dir:
            self.status_label.config(text="Por favor selecciona rutas válidas.")
            return

        try:
            ch_controller = CHController()
            ch_controller.generar_ch(input_dir, output_dir, selected_format)
            messagebox.showinfo("Éxito", f"Archivos CH generados correctamente en formato {selected_format}.")
        except Exception as e:
            self.status_label.config(text=f"Error al generar CH: {str(e)}")

    def generar_dh(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        selected_format = self.file_format.get()  # Obtener el formato seleccionado (mseed o seg2)

        if not input_dir or not output_dir:
            self.status_label.config(text="Por favor selecciona rutas válidas.")
            return

        try:
            dh_controller = DHController()
            dh_controller.generar_dh(input_dir, output_dir, selected_format)
            messagebox.showinfo("Éxito", f"Archivos DH generados correctamente en formato {selected_format}.")
        except Exception as e:
            self.status_label.config(text=f"Error al generar DH: {str(e)}")
