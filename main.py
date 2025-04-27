from TextToSound import *
from SoundToText import *
from MergeWithTrack  import *





text = "///YA HUESOS///"
text_to_sound(text, "output.wav")
decoded_text = sound_to_text("output.wav")
print(f"Исходный текст: {text}")
print(f"Декодированный текст: {decoded_text}")
msglength = MergeSound(morse_wav_path = "output.wav", background_wav_path = "Test2.wav")
second_text = sound_to_text("Result.wav", msglength)
print(f"Тест с треком: {second_text}")
