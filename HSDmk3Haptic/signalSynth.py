import numpy as np
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import wave
import os
from presetTouch import PresetsTouch
from scipy.io import wavfile

class SignalSynth:
    def __init__(self, sampleRate=48000):
        self.sampleRate = sampleRate
        self.duration = 2.0
        self.waveform = None
        self.freq = 100.0
        self.amp = 0.1
        self.signalType = "Sinusoïdal"
        self.modulationType = "Aucune"
    
    def configureSignalFromPreset(self, preset):
        self.signalType = preset.signal
        self.modulationType = preset.modulation
        self.freq = preset.freq
        self.amp = preset.amp
        self.duration = preset.duration
        return self.generateSignal(preset)
    

    def loadWav(self, filepath):
        fs, audio_data = wavfile.read(filepath)

        # Convertir en float32
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        elif audio_data.dtype == np.int32:
            audio_data = audio_data.astype(np.float32) / 2147483648.0
        elif audio_data.dtype == np.uint8:
            audio_data = (audio_data.astype(np.float32) - 128) / 128.0

        # Si stéréo, faire une moyenne (mono)
        if len(audio_data.shape) == 2:
            audio_data = np.mean(audio_data, axis=1)

        duration = audio_data.shape[0] / fs

        return audio_data, fs, duration

    def generateSignal(self, preset):
        if os.path.isfile(self.signalType):
            try:
                audio_signal, fs, duration = self.loadWav(self.signalType)

                self.sampleRate = fs
                self.duration = duration
                preset.duration = self.duration  # Mettre à jour la durée dans le preset

                # Recréer l'axe temporel avec la vraie durée
                self.t = np.linspace(0, self.duration, int(self.sampleRate * self.duration), endpoint=False)

                self.waveform = self.amp * audio_signal

                self.waveform = self.lowpassFilter(self.waveform, 1000, self.sampleRate)

                if len(self.waveform) > len(self.t):
                    self.waveform = self.waveform[:len(self.t)]
                elif len(self.waveform) < len(self.t):
                    self.waveform = np.pad(self.waveform, (0, len(self.t) - len(self.waveform)), 'constant')

            except Exception as e:
                raise ValueError(f"Erreur lors de la lecture du fichier audio : {e}")
        else:
            # Sinon, comportement normal
            self.t = np.linspace(0, self.duration, int(self.sampleRate * self.duration), endpoint=False)

            if self.signalType == "Sinusoïdale":
                self.waveform = self.amp * np.sin(2 * np.pi * self.freq * self.t)
            elif self.signalType == "Bruit Blanc":
                self.waveform = self.amp * np.random.normal(0, 10, len(self.t))
                self.waveform = self.lowpassFilter(self.waveform, self.freq, self.sampleRate)
            elif self.signalType == "Tap":
                interval = 0.5
                pulse_duration = 0.01
                num_pulses = 3
                pulse_spacing = 0.01
                self.waveform = np.zeros_like(self.t)
                for i in range(len(self.t)):
                    for j in range(num_pulses):
                        if (i / self.sampleRate) % interval < pulse_duration + j * pulse_spacing:
                            self.waveform[i] = self.amp
            elif self.signalType == "Mixte":
                sinWave = self.amp * np.sin(2 * np.pi * self.freq * self.t)
                noise = self.amp * np.random.normal(0, 10, len(self.t))
                noise = self.lowpassFilter(noise, 500, self.sampleRate)
                self.waveform = sinWave + noise
            else:
                raise ValueError(f"Type de signal non supporté: {self.signalType}")

        self.waveform *= self.applyModulation()

        return self.t, self.waveform


    def applyModulation(self):
        if self.modulationType == "Aucune":
            return np.ones_like(self.t)
        elif self.modulationType == "Sinusoïdale":
            modulation = 0.5 * (1 + np.sin(2 * np.pi * 0.5 * self.t))
            return modulation
        elif self.modulationType == "Impulsion":
            attack_time = 0.01  
            decay_time = 0.05    
            mod_signal = np.zeros_like(self.t)
            mod_signal[self.t < attack_time] = self.t[self.t < attack_time] / attack_time
            mod_signal[(self.t >= attack_time) & (self.t < attack_time + decay_time)] = 1 - ((self.t[(self.t >= attack_time) & (self.t < attack_time + decay_time)] - attack_time) / decay_time)
            return mod_signal
        elif self.modulationType == "Fade In/Out":
            # Modulation de type fade in/out
            fade_in_time = 0.1  # Temps de fade in
            fade_out_time = 0.1  # Temps de fade out
            mod_signal = np.ones_like(self.t)
            fade_in = (self.t < fade_in_time)
            fade_out = (self.t > (self.t[-1] - fade_out_time))
            mod_signal[fade_in] = self.t[fade_in] / fade_in_time
            mod_signal[fade_out] = (self.t[-1] - self.t[fade_out]) / fade_out_time
            return mod_signal
        else:
            raise ValueError(f"Type de modulation non supporté: {self.modulationType}")

    def lowpassFilter(self, data, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = lfilter(b, a, data)
        return y


if __name__ == "__main__":
    synth = SignalSynth()
    presets = PresetsTouch()

    # Exemple de configuration d'un signal à partir d'un preset
    # preset1 = presets.Carresse1
    # preset2 = presets.Carresse2
    # preset3 = presets.Carresse3
    # preset4 = presets.Carresse4
    # preset5 = presets.Carresse5
    # preset6 = presets.Carresse6
    # preset7 = presets.CarresseTest
    # preset8 = presets.Carresse8

    # preset1 = presets.Frottement1
    # preset2 = presets.Frottement2
    # preset3 = presets.Frottement3
    # preset4 = presets.Frottement4
    # preset5 = presets.Frottement5
    # preset6 = presets.Frottement6
    # preset7 = presets.Frottement7
    # preset8 = presets.Frottement8

    preset1 = presets.CaresseExpe1
    preset2 = presets.CaresseExpe2
    preset3 = presets.FrottementExpe1
    preset4 = presets.FrottementExpe2
    preset5 = presets.TapotementExpe1
    preset6 = presets.TapotementExpe2
    preset7 = presets.FrappeExpe

    # Charger tous les presets de type "Carresse"
    carresse_presets = [preset1, preset2, preset3, preset4, preset5, preset6, preset7]

    # Créer un subplot pour chaque preset
    num_presets = len(carresse_presets)
    fig, axes = plt.subplots(num_presets, 1, figsize=(10, 5 * num_presets))

    if num_presets == 1:
        axes = [axes]  # S'assurer que axes est une liste même pour un seul subplot

    for i, preset in enumerate(carresse_presets):
        t, waveform = synth.configureSignalFromPreset(preset)
        axes[i].plot(t, waveform)
        axes[i].set_title(f"Waveform: {synth.signalType} with {synth.modulationType} modulation (Preset: {i})")
        axes[i].set_xlabel("Time [s]")
        axes[i].set_ylabel("Amplitude")
        axes[i].grid(True)

    plt.tight_layout()
    plt.show()




    
    