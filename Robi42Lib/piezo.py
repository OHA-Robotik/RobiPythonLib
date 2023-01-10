from machine import Pin, PWM
from time import sleep_ms
from uasyncio import sleep_ms as sleep_ms_async
import Robi42Lib.notes_and_freqs as naf


class Piezo:
    def __init__(self):
        self.piezo = PWM(Pin(22, Pin.OUT))
        self.piezo.freq(440)
        self.piezo.duty_u16(0)

    def play_tone(self, tone: "Tone"):
        self.piezo.duty_u16(512)
        self.piezo.freq(tone.freq)
        sleep_ms(tone.duration_ms)
        self.piezo.duty_u16(0)

    def play_tones(self, tones: list["Tone"]):
        for tone in tones:
            self.piezo.duty_u16(512)
            self.piezo.freq(tone.freq)
            sleep_ms(tone.duration_ms)
        self.piezo.duty_u16(0)

    async def play_tone_async(self, tone: "Tone"):
        self.piezo.duty_u16(512)
        self.piezo.freq(tone.freq)
        await sleep_ms_async(tone.duration_ms)
        self.piezo.duty_u16(0)

    async def play_tones_async(self, tones: list["Tone"]):
        for tone in tones:
            self.piezo.duty_u16(512)
            self.piezo.freq(tone.freq)
            await sleep_ms_async(tone.duration_ms)
        self.piezo.duty_u16(0)

    def _turn_off(self):
        self.piezo.duty_u16(0)
        self.piezo.deinit()


class Tone:
    def __init__(self, note: str, freq: int, duration_ms: int = 200):
        """
        Create a tone
        freq: Frequency
        """
        self.note, self.freq, self.duration_ms = note, freq, duration_ms


class SampleTones:
    tones = sorted(
        [Tone(n, int(f)) for n, f in naf.tones.items()], key=lambda x: x.freq
    )

    @staticmethod
    def get_tone(note: str) -> Tone:
        return Tone(note, naf.tones[note])
