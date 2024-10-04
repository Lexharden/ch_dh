import os
import logging
from controllers.mseed_generator import process_files_dh

class DHController:
    def __init__(self):
        pass

    def generar_dh(self, input_dir, output_dir, file_format):
        """Genera los archivos DH en el directorio de salida en el formato especificado"""
        logging.info(f"Generación de archivos DH iniciada. Directorio de entrada: {input_dir}, Directorio de salida: {output_dir}")

        if not os.path.exists(input_dir):
            error_message = f"El directorio de entrada no existe: {input_dir}"
            logging.error(error_message)
            raise ValueError(error_message)

        if not os.path.exists(output_dir):
            error_message = f"El directorio de salida no existe: {output_dir}"
            logging.error(error_message)
            raise ValueError(error_message)

        try:
            # Definir las extensiones de archivos DH
            file_extensions_vertical = ['1.seg2']  # Archivo para el canal vertical
            file_extensions = ['2.seg2', '3.seg2']  # Archivos para los canales X e Y

            # Procesar los archivos DH y guardar en el directorio de salida
            process_files_dh(input_dir, file_extensions_vertical, file_extensions, output_dir, file_format)

            logging.info(f"Generación de archivos DH completada con éxito en formato {file_format}.")
        except Exception as e:
            logging.error(f"Error al generar archivos DH: {str(e)}")
            raise e
