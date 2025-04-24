from TextToSound import *


def MergeSound(NameWAV1, NameWAV2, output = "Result.wav")-> int:
    # Читаем первый файл
    with wave.open(NameWAV1, 'rb') as wf1:
        params = wf1.getparams()
        data1 = np.frombuffer(wf1.readframes(wf1.getnframes()), dtype=np.int16)

    # Читаем второй файл
    with wave.open(NameWAV2, 'rb') as wf2:
        data2 = np.frombuffer(wf2.readframes(wf2.getnframes()), dtype=np.int16)

    # Создаем массив для результата (длина = максимальная из двух)
    max_len = max(len(data1), len(data2))
    mixed = np.zeros(max_len, dtype=np.int32)

    # Накладываем оба трека (автоматическое дополнение нулями)
    mixed[:len(data1)] += data1
    mixed[:len(data2)] += data2

    # Нормализация и преобразование типа
    mixed = np.int16(mixed / np.max(np.abs(mixed)) * 32767)

    # Записываем результат
    with wave.open(output, 'wb') as wf_out:
        wf_out.setparams(params)
        wf_out.writeframes(mixed.tobytes())

    return min(len(data1), len(data2)) #Возвращаем длину меньшего из файлов, чтобы при расшифровке можно было прерваться где надо