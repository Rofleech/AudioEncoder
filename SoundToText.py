from TextToSound import *


def detect_frequency(chunk, area):
    """Определение доминирующей частоты в аудиочанке с помощью Быстрого Преобразования Фурье"""

    yf = np.fft.rfft(chunk) #Берём звуковой чанк, преобразованный заранее в массив чисел и получаем список силы(громкости) частот по порядку
    xf = np.fft.rfftfreq(len(chunk), 1 / fs) #на выходе - Шкала(список) частот по порядку с их силой xf[0] = 0 - сила нулевой частоты

    MyIdx = np.argmax(xf >= area)
    idx = np.argmax(np.abs(yf[MyIdx:])) +  MyIdx # пропускаем первые area элементов, ищем строго выше нужной частоты

    if MyIdx == 0 and xf[0] < area: #Если на данной частоте ничего нет, то возвращаем None
        return 0

    return xf[idx]


def sound_to_text(filename="sound_output.wav", length = 0):
    """Обратное преобразование звука в текст"""
    # Открываем WAV файл
    with wave.open(filename, 'rb') as wf:
        # Получаем параметры аудио
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()

        # Читаем все кадры
        frames = wf.readframes(n_frames)

    # Конвертируем в numpy массив
    audio_data = np.frombuffer(frames, dtype=np.int16)
    audio_data = audio_data.astype(np.float32) / 32767.0

    # Размер чанка для анализа (соответствует длительности бита)
    chunk_size = int(fs * bit_duration)
    silence_chunk_size = int(fs * silence_duration)

    text = ""
    bits = []
    i = 0

    # При работе с "Вшитым" в трек сообщением нам нужно дождаться конца сообщения, а не трека, поэтому переменную длины можно получить на входе
    if length == 0:
        length = len(audio_data)

    # Пропускаем начальный шум
    while i < length - chunk_size:
        # Анализируем текущий чанк
        chunk = audio_data[i:i + chunk_size]
        freq = detect_frequency(chunk, area)

        # Определяем бит по частоте
        if freq > freq_threshold:
            bit = 1
        else:
            bit = 0

        # Проверяем стартовый бит (должен быть 1)
        if len(bits) == 0 and bit == 1:
            bits.append(bit)
            i += chunk_size + silence_chunk_size
            continue

        # Собираем биты (8 бит + стоповый бит)
        if 0 < len(bits) <= 8:
            bits.append(bit)
            i += chunk_size + silence_chunk_size
        else:
            # Если собрали 9 бит (8 данных + 1 стоповый)
            if len(bits) == 9:
                # Извлекаем ASCII код (игнорируем стартовый и стоповый биты)
                ascii_code = 0
                for j in range(8):
                    ascii_code |= (bits[j + 1] << (7 - j))

                # Добавляем символ в результат
                text += chr(ascii_code)
                bits = []

            i += chunk_size

    return text

