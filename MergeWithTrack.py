from TextToSound import *


def MergeSound(morse_wav_path, background_wav_path, output_path = "Result.wav", use_left_channel = False)->int:
    # 1. Загружаем морзянку (моно)
    with wave.open(morse_wav_path, 'rb') as morse_wav:
        morse_data = np.frombuffer(morse_wav.readframes(morse_wav.getnframes()),
                                   dtype=np.int16)
        morse_sr = morse_wav.getframerate()

    # 2. Загружаем фон (конвертируем в моно, если нужно)
    with wave.open(background_wav_path, 'rb') as bg_wav:
        bg_params = bg_wav.getparams()
        bg_data = np.frombuffer(bg_wav.readframes(bg_wav.getnframes()),
                                dtype=np.int16)
        bg_sr = bg_wav.getframerate()

        # Конвертируем стерео в моно (берём левый канал)
        if bg_params.nchannels == 2:
            bg_data = bg_data.reshape(-1, 2)[:, 0]

    # 3. Проверка частоты дискретизации
    if morse_sr != bg_sr:
        print("Частоты дискретизации не совпадают!")

    # 4. Снижаем громкость морзянки перед смешиванием (чтобы избежать клиппинга)
    morse_volume = 0.1  # 30% от максимальной громкости (можно регулировать)
    morse_data = (morse_data*morse_volume).astype(np.int16)

    # 5. Накладываем морзянку на фон (без нормализации!)
    mixed_data = bg_data.copy()
    mixed_data[:len(morse_data)] += morse_data

    # 6. Сохраняем результат (моно)
    with wave.open(output_path, 'wb') as out_wav:
        out_wav.setparams((
            1,  # моно
            bg_params.sampwidth,
            bg_params.framerate,
            len(mixed_data),
            bg_params.comptype,
            bg_params.compname
        ))
        out_wav.writeframes(mixed_data.tobytes())

    print(f"Результат сохранён в {output_path}")
    return len(morse_data)