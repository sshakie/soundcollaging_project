import pygame, soundfile, time
from scipy.signal import resample
from io import BytesIO

pygame.mixer.init()
pygame.mixer.set_num_channels(50)


class SoundManager:
    def __init__(self, path):
        self.sound = pygame.mixer.Sound(path)
        self.data, self.samplerate = soundfile.read(path)

        # Для записи
        self.is_recording = False
        self.recorded_notes = []
        self.timestamps = []

    def play(self):
        self.sound.play()

    def play_delayed(self, poss,
                     gl_volume):  # Для проигрывания с задержкой программы (я не придумал больше никак реализовать старт не с начала)
        self.sound.set_volume(0)
        self.sound.play()
        pygame.time.delay(poss)
        self.sound.set_volume(gl_volume)

    def play_note(self, cents):  # Воспроизведение нот, когда играешь на миди клавиатуре
        speed = 2 ** (cents / 1200)
        range_cut = int(len(self.data) / speed)
        new_data = resample(self.data, range_cut)  # здесь рестречится звук чтобы повысить тон (благодаря scipy)
        memory = BytesIO()
        soundfile.write(memory, new_data, self.samplerate, format='WAV')
        memory.seek(0)

        sound = pygame.mixer.Sound(memory)
        sound.play()

        if self.is_recording:  # сохранение данных для сохранения, если запись включена
            self.recorded_notes.append(new_data)
            self.timestamps.append(time.time())

    def stop(self):  # останавливает звук
        self.sound.stop()

    def set_volume(self, new_volume):  # ставится новую громкость звуку
        self.sound.set_volume(new_volume)

    def get_audio_duration(self):  # узнает длительность звука
        return self.sound.get_length()

    def start_recording(self):  # Начало записи миди клавиатуры + очищение старых данных
        self.is_recording = True
        self.recorded_notes = []
        self.timestamps = [time.time()]

    def stop_recording(self, save_path):  #
        if self.is_recording:
            self.is_recording = False
            if self.recorded_notes:
                total_duration = self.timestamps[-1] - self.timestamps[0] + len(
                    self.recorded_notes[-1]) / self.samplerate  # здесь высчитывается время сколько записывали игру
                output = [0] * int(total_duration * self.samplerate)

                for note, timestamp in zip(self.recorded_notes, self.timestamps[1:]):
                    start = int((timestamp - self.timestamps[0]) * self.samplerate)
                    if len(note.shape) > 1:  # Если звук в стерео, то берем только один канал, чтобы сделать звук в моно
                        note = note[:, 0]
                    end = start + len(note)
                    output[start:end] = [x + y for x, y in zip(output[start:end],
                                                               note)]  # это нужно было для того чтобы звуки ложились друг на друга (складываем амплитуды)

                starting_from = 0
                for i, v in enumerate(output):  # ищем где начинается звук и обрезаем все с этого момента
                    if v != 0:
                        starting_from = i
                        break
                output = output[starting_from:]
                soundfile.write(save_path, output, self.samplerate)
