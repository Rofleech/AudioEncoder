import pyaudio
import numpy as np
import wave

# Настройки звука
volume = 0.5  # от 0.0 до 1.0
fs = 44100  # частота дискретизации
zero_frequency = 20000  # базовая частота звука (в Гц)
one_frequency = 21000


# Длительности сигналов
bit_duration = 0.2  # длительность одного бита (в секундах)
silence_duration = bit_duration/2

freq_threshold = (zero_frequency + one_frequency) / 2

def generate_tone(frequency, duration):
    """Генерация тона заданной частоты и длительности"""
    t = np.arange(int(fs * duration))
    signal = volume * np.sin(2 * np.pi * frequency * t / fs)
    return signal.astype(np.float32)


def generate_silence(duration):
    """Генерация тишины заданной длительности"""
    return np.zeros(int(fs * duration), dtype=np.float32)


def char_to_sound(char):
    """Преобразование символа в последовательность звуковых сигналов"""
    # Получаем ASCII код символа
    ascii_code = ord(char)

    # Преобразуем в 8 бит (старший бит первый)
    bits = [(ascii_code >> i) & 1 for i in range(7, -1, -1)]

    # Генерируем звуки для каждого бита
    sound_sequence = []

    # Добавляем стартовый бит (1) для синхронизации
    sound_sequence.append(generate_tone(one_frequency, bit_duration))
    sound_sequence.append(generate_silence(bit_duration / 2))

    # Добавляем биты символа
    for bit in bits:
        if bit:
            # Для 1 - высокий тон
            sound_sequence.append(generate_tone(one_frequency, bit_duration))
        else:
            # Для 0 - низкий тон
            sound_sequence.append(generate_tone(zero_frequency, bit_duration))
        sound_sequence.append(generate_silence(bit_duration / 2))

    # Добавляем стоповый бит (1)
    sound_sequence.append(generate_tone(one_frequency, bit_duration))

    return np.concatenate(sound_sequence)


def text_to_sound(text, filename="sound_output.wav"):
    """Преобразование текста в звуковую последовательность"""
    p = pyaudio.PyAudio()
    all_frames = np.array([], dtype=np.float32)


    for char in text:
        # Пропускаем символы, которые не можем закодировать
        if ord(char) > 255:
            continue

        # Генерируем звук для символа
        char_sound = char_to_sound(char)
        all_frames = np.append(all_frames, char_sound)

        # Добавляем паузу между символами
        all_frames = np.append(all_frames, generate_silence(bit_duration * 2))

    # Воспроизведение
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs, output=True)
    stream.write(all_frames)
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Сохранение в файл WAV
    all_frames = (all_frames * 32767).astype(np.int16)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16 бит = 2 байта
        wf.setframerate(fs)
        wf.writeframes(all_frames.tobytes())
    print(f"Аудио сохранено в файл: {filename}")


def detect_frequency(chunk):
    """Определение доминирующей частоты в аудиочанке с помощью FFT (numpy версия)"""
    # Применяем FFT (используем numpy вместо scipy)
    yf = np.fft.rfft(chunk)
    xf = np.fft.rfftfreq(len(chunk), 1 / fs)

    # Находим индекс максимальной амплитуды (исключаем очень низкие частоты)
    idx = np.argmax(np.abs(yf[10:])) + 10  # пропускаем первые 10 элементов

    # Возвращаем соответствующую частоту
    return xf[idx]


def sound_to_text(filename="sound_output.wav"):
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

    # Пропускаем начальный шум
    while i < len(audio_data) - chunk_size:
        # Анализируем текущий чанк
        chunk = audio_data[i:i + chunk_size]
        freq = detect_frequency(chunk)

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


text = "///HUESOS???GAY???FEMBOY"
text_to_sound(text, "output.wav")
decoded_text = sound_to_text("output.wav")
print(f"Исходный текст: {text}")
print(f"Декодированный текст: {decoded_text}")