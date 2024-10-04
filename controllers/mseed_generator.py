import os
import logging
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


def create_mseed(channel_data, output_filename, sampling_rate, sample_interval, prefix, output_dir):
    """Crea un archivo MiniSEED con los datos del canal especificado y cambia la frecuencia de muestreo."""
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
        output_filename = f"{prefix}_{output_filename}"  # Agregar el prefijo al nombre del archivo
        output_path = os.path.join(output_dir, output_filename)  # Guardar en el directorio de salida
        stream.write(output_path, format='MSEED')
        logging.info(f"Archivo MiniSEED creado: {output_path}")
    else:
        logging.warning(f"Stream vacío, no se creó el archivo: {output_filename}")


def process_files_ch(directory, file_extensions_ch, output_dir):
    """Procesa los archivos CH y genera archivos MiniSEED con el prefijo 'CH'."""
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

        # Crear archivos MiniSEED para los canales X
        create_mseed(channel_data_2, f'Channel_X_{ext}.mseed', sampling_rate_2, sample_interval_2, 'CH', output_dir)

        # Crear archivos MiniSEED para los canales Y
        create_mseed(channel_data_3, f'Channel_Y_{ext}.mseed', sampling_rate_3, sample_interval_3, 'CH', output_dir)


def process_files_dh(directory, file_extensions_vertical, file_extensions, output_dir):
    """Procesa los archivos DH y genera archivos MiniSEED con el prefijo 'DH', incluyendo dos para X, dos para Y, y uno para V."""
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

        create_mseed(channel_data_1, f'Channel_V_{ext}.mseed', sampling_rate_1, sample_interval_1, 'DH', output_dir)

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

        # Crear archivos MiniSEED para los canales X
        create_mseed(channel_data_2, f'Channel_X_{ext}.mseed', sampling_rate_2, sample_interval_2, 'DH', output_dir)

        # Crear archivos MiniSEED para los canales Y
        create_mseed(channel_data_3, f'Channel_Y_{ext}.mseed', sampling_rate_3, sample_interval_3, 'DH', output_dir)
