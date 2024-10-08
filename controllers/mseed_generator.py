import os
import logging
import subprocess

from obspy import Stream, Trace, read


def read_files(directory, file_extension):
    """Lee los archivos en el directorio especificado que terminan con la extensión dada."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(file_extension)]


def filter_channel_data(files, channel_number):
    """Filtra los datos de los archivos para el canal especificado y devuelve los datos junto con la frecuencia de muestreo."""
    channel_data = []
    sampling_rates = set()
    sample_interval = set()
    for filename in files:
        try:
            st = read(filename)
            for tr in st:
                if tr.stats.seg2.CHANNEL_NUMBER == channel_number:
                    tr.stats.seg2.SAMPLE_INTERVAL = float(tr.stats.seg2.SAMPLE_INTERVAL)
                    channel_data.append((tr.data, os.path.basename(filename)))
                    sampling_rates.add(tr.stats.sampling_rate)
                    sample_interval.add(float(tr.stats.seg2.SAMPLE_INTERVAL))
        except Exception as e:
            logging.error(f"Error al leer el archivo {filename}: {str(e)}")

    if len(sampling_rates) != 1:
        error_message = f"Se encontraron múltiples frecuencias de muestreo: {sampling_rates}"
        logging.error(error_message)
        raise ValueError(error_message)

    return channel_data, sampling_rates.pop(), sample_interval.pop()


def create_file(channel_data, output_filename, sampling_rate, sample_interval, prefix, output_dir, file_format):
    """Crea un archivo en formato MSEED y lo convierte a SEG2 si es necesario."""
    if not channel_data:
        logging.warning(f"No se encontraron datos para crear {output_filename}.")
        return

    stream = Stream()
    for data, filename in channel_data:
        tr = Trace(data=data)
        tr.stats.station = filename
        tr.stats.sampling_rate = sampling_rate
        tr.stats.delta = sample_interval
        stream.append(tr)

    if stream:
        # Crear archivo MSEED temporal
        temp_mseed_filename = f"{prefix}_{output_filename.replace('.mseed', '').replace('.msd', '')}.mseed"
        temp_mseed_path = os.path.join(output_dir, temp_mseed_filename)

        # Escribir el archivo MSEED
        stream.write(temp_mseed_path, format='MSEED')
        logging.info(f"Archivo MSEED creado: {temp_mseed_path}")

        # Si se solicita convertir a SEG2, realizar la conversión y eliminar el archivo MSEED
        if file_format == "seg2":
            convert_to_seg2(temp_mseed_path)
            # Eliminar el archivo MSEED después de la conversión a SEG2
            if os.path.exists(temp_mseed_path):
                os.remove(temp_mseed_path)
                logging.info(f"Archivo MSEED eliminado: {temp_mseed_path}")
            else:
                logging.error(f"Archivo MSEED no encontrado para eliminar: {temp_mseed_path}")
        else:
            # Si se seleccionó formato MSEED o MSD, se queda con el archivo MSEED
            logging.info(f"Archivo MSEED final: {temp_mseed_path}")
    else:
        logging.warning(f"Stream vacío, no se creó el archivo: {output_filename}")


def convert_to_seg2(input_mseed):
    """Convierte un archivo MSEED a SEG2 usando Geopsy."""
    try:
        # Nombre del archivo de salida con la extensión .seg2
        output_seg2 = input_mseed.replace('.mseed', '.seg2')

        # Ruta al ejecutable geopsy en tu sistema
        geopsy_path = r'C:\geopsypack\bin\geopsy.exe'

        # Usar os.path.normpath para asegurar que las rutas estén correctas en Windows
        output_seg2 = os.path.normpath(output_seg2)
        input_mseed = os.path.normpath(input_mseed)

        # Comando para ejecutar Geopsy
        command = [geopsy_path, '-export', output_seg2, '-export-format', 'Seg2', input_mseed]

        # Ejecutar el comando usando subprocess
        logging.info(f"Ejecutando comando: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info(f"Archivo SEG-2 creado: {output_seg2}")

    except subprocess.CalledProcessError as e:
        logging.error(f"Error al convertir a SEG-2: {str(e)}")
        logging.error(f"Salida del comando: {e.output}")
    except FileNotFoundError as fnf_error:
        logging.error(f"Archivo no encontrado: {fnf_error}")


def process_files_ch(directory, file_extensions_ch, output_dir, file_format):
    """Procesa los archivos CH y genera archivos con el formato especificado (mseed o seg2) con el prefijo 'CH'."""
    for ext in file_extensions_ch:
        lateral_files = read_files(directory, ext)
        if not lateral_files:
            logging.warning(f"No se encontraron archivos con extensión {ext} en el directorio {directory}.")
            continue

        try:
            channel_data_2, sampling_rate_2, sample_interval_2 = filter_channel_data(lateral_files, '2')  # Canal lado X
            channel_data_3, sampling_rate_3, sample_interval_3 = filter_channel_data(lateral_files, '3')  # Canal lado Y
        except ValueError as e:
            logging.error(f"Error procesando los archivos con extensión {ext}: {str(e)}")
            continue

        # Crear archivos con el formato especificado para los canales X
        create_file(channel_data_2, f'Channel_X_{ext}.mseed', sampling_rate_2, sample_interval_2, 'CH', output_dir,
                    file_format)

        # Crear archivos con el formato especificado para los canales Y
        create_file(channel_data_3, f'Channel_Y_{ext}.mseed', sampling_rate_3, sample_interval_3, 'CH', output_dir,
                    file_format)


def process_files_dh(directory, file_extensions_vertical, file_extensions, output_dir, file_format):
    """Procesa los archivos DH y genera archivos con el formato especificado (mseed o seg2) con el prefijo 'DH', incluyendo dos para X, dos para Y, y uno para V."""
    # Generar archivo para el canal vertical (V)
    for ext in file_extensions_vertical:
        vertical_files = read_files(directory, ext)
        if not vertical_files:
            logging.warning(f"No se encontraron archivos con extensión {ext} en el directorio {directory}.")
            continue

        try:
            channel_data_1, sampling_rate_1, sample_interval_1 = filter_channel_data(vertical_files,
                                                                                     '1')  # Canal vertical (V)
        except ValueError as e:
            logging.error(f"Error procesando los archivos con extensión {ext}: {str(e)}")
            continue

        create_file(channel_data_1, f'Channel_V_{ext}.mseed', sampling_rate_1, sample_interval_1, 'DH', output_dir,
                    file_format)

    # Generar archivos para los canales X e Y
    for ext in file_extensions:
        lateral_files = read_files(directory, ext)
        if not lateral_files:
            logging.warning(f"No se encontraron archivos con extensión {ext} en el directorio {directory}.")
            continue

        try:
            channel_data_2, sampling_rate_2, sample_interval_2 = filter_channel_data(lateral_files, '2')  # Canal lado X
            channel_data_3, sampling_rate_3, sample_interval_3 = filter_channel_data(lateral_files, '3')  # Canal lado Y
        except ValueError as e:
            logging.error(f"Error procesando los archivos con extensión {ext}: {str(e)}")
            continue

        # Crear archivos con el formato especificado para los canales X
        create_file(channel_data_2, f'Channel_X_{ext}.mseed', sampling_rate_2, sample_interval_2, 'DH', output_dir,
                    file_format)

        # Crear archivos con el formato especificado para los canales Y
        create_file(channel_data_3, f'Channel_Y_{ext}.mseed', sampling_rate_3, sample_interval_3, 'DH', output_dir,
                    file_format)
