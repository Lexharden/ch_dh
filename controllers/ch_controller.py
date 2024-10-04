import os
import logging
from controllers.mseed_generator import process_files_ch

class CHController:
    def __init__(self):
        pass

    def generar_ch(self, input_dir, output_dir):
        """Genera los archivos CH en el directorio de salida"""
        logging.info(f"Generación de archivos CH iniciada. Directorio de entrada: {input_dir}, Directorio de salida: {output_dir}")

        if not os.path.exists(input_dir):
            error_message = f"El directorio de entrada no existe: {input_dir}"
            logging.error(error_message)
            raise ValueError(error_message)

        if not os.path.exists(output_dir):
            error_message = f"El directorio de salida no existe: {output_dir}"
            logging.error(error_message)
            raise ValueError(error_message)

        try:
            # Definir las extensiones de archivos CH
            file_extensions = ['2.seg2', '3.seg2']

            # Procesar los archivos CH y guardar en el directorio de salida
            process_files_ch(input_dir, file_extensions, output_dir)

            logging.info("Generación de archivos CH completada con éxito.")
        except Exception as e:
            logging.error(f"Error al generar archivos CH: {str(e)}")
            raise e
