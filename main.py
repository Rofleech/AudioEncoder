from TextToSound import *
from SoundToText import *
from MergeWithTrack  import *





text = "SOS"
text_to_sound(text, "output.wav")
decoded_text = sound_to_text("output.wav")
print(f"Исходный текст: {text}")
print(f"Декодированный текст: {decoded_text}")
msglength = MergeSound(NameWAV1 = "output.wav", NameWAV2 = "Test1.wav")
second_text = sound_to_text("Result.wav", msglength)
print(f"Тест с треком: {second_text}")
