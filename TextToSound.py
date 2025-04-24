import pyaudio
import numpy as np
import wave

# Настройки звука
volume = 1  # от 0.0 до 1.0
fs = 44100  # частота дискретизации
zero_frequency = 19000  # базовая частота звука (в Гц)
one_frequency = 19900


# Длительности сигналов
bit_duration = 0.2  # длительность одного бита (в секундах)
silence_duration = bit_duration/2

freq_threshold = (zero_frequency + one_frequency) / 2
area = min(zero_frequency,one_frequency) - 1 #Ограничение по нижним частотам для поиска ТОЛЬКО закодированных звуков

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
