import sounddevice as sd
import numpy as np
import time

class PlaySignal:
    def __init__(self, signalSynth, patternManager, activePorts, mappingIntensity):
        self.activePorts = activePorts  
        self.numChannels = len(activePorts)

        self.signalSynth = signalSynth
        self.patternManager = patternManager
        self.waveform = self.signalSynth.waveform  
        self.logIntensity = self.patternManager.logIntensity  
        self.mappingIntensity = mappingIntensity 

        self.sample_rate = 48000
        self.allChannels = 20  
        self.deviceList, self.defaultDevice = self.detectDevices()
        if len(self.deviceList) >= 2:
            self.defaultDevice = list(self.deviceList.keys())[1]


    def detectDevices(self):
        """Détecte les périphériques audio compatibles avec 20 canaux"""
        devices = sd.query_devices()
        device_list = {d["name"]: d["index"] for d in devices if "max_output_channels" in d and d["max_output_channels"] >= self.allChannels}
        
        if not device_list:
            device_list = {d["name"]: d["index"] for d in devices if "max_output_channels" in d and d["max_output_channels"] >= self.numChannels}
            if device_list:
                print(f"Aucun périphérique avec {self.allChannels} canaux trouvé. Utilisation de périphériques avec {self.numChannels} canaux minimum.")
            else:
                print("Aucun périphérique compatible trouvé.")
        
        if device_list:
            print(f"Périphériques trouvés : {list(device_list.keys())}")
        default_device = list(device_list.keys())[0] if device_list else ""
        return device_list, default_device

    def signalWithIntensities(self):
        waveformSample = len(self.waveform) // self.logIntensity.shape[1]
        signal = np.zeros((len(self.waveform), self.allChannels))

        for step in range(self.logIntensity.shape[1]):
            start = step * waveformSample
            end = start + waveformSample
            
            for keyIntensity, indexPort in self.mappingIntensity.items():
                try:
                    indexIntensity = int(keyIntensity[1:]) - 1  
                    
                    if indexIntensity >= 0 and indexIntensity < self.logIntensity.shape[0]:
                        actualChannel = self.activePorts[indexPort]  
                        
                        stepIntensity = self.logIntensity[indexIntensity, step]
                        signal[start:end, actualChannel] = self.waveform[start:end] * stepIntensity
                    else:
                        print(f"Avertissement: Indice d'intensité {indexIntensity} hors limites pour {keyIntensity}")
                except (ValueError, IndexError) as e:
                    print(f"Erreur lors du traitement de {keyIntensity}: {e}")

        return signal

    def playSignal(self):
        if not self.deviceList:
            print("Aucun périphérique audio compatible trouvé.")
            return

        signal = self.signalWithIntensities()
        
        deviceInfo = sd.query_devices(self.deviceList[self.defaultDevice])
        availableChannels = deviceInfo['max_output_channels']
        
        if availableChannels < self.allChannels:
            print(f"Attention: Le périphérique sélectionné n'a que {availableChannels} canaux de sortie (20 requis)")
            # Tronquer le signal pour n'utiliser que les canaux disponibles
            signal = signal[:, :availableChannels]
        
        print(f"Lecture du signal sur les canaux {self.activePorts} du périphérique {self.defaultDevice}")
        
        sd.play(signal, 
                samplerate=self.sample_rate, 
                device=self.deviceList[self.defaultDevice], 
                blocking=True)

    def stopSignal(self):
        sd.stop()


# Exemple d'utilisation
# if __name__ == "__main__":
    # from signalSynth import SignalSynth
    # from patternManager import PatternManager
    # from presetTouch import PresetsTouch

    # signal_synth = SignalSynth()
    # presets = PresetsTouch()
    # pattern_manager = PatternManager()

    # # Les canaux spécifiques à utiliser parmi les 20 disponibles
    # activePorts = [0, 1, 4, 5, 6, 7]  # Par exemple, canaux 1, 2, 5, 6, 7, 8
    
    # # Mappage entre les intensités et les indices dans activePorts
    # mappingIntensity = {
    #     "I1": 1,  # I1 -> port2
    #     "I2": 5,  # I2 -> port8
    #     "I3": 0,  # I3 -> port1
    #     "I4": 4,  # I4 -> port7
    #     "I5": 3,  # I5 -> port6
    #     "I6": 2,  # I6 -> port5
    # }

    # # Configuration du signal et du pattern (même preset pour la cohérence)
    # preset = presets.Frottement
    # signal_synth.configureSignalFromPreset(preset)
    # pattern_manager.configurePatternFromPreset(preset)
    
    # # Générer le pattern d'intensité
    # pattern_manager.adjustPatternSpeed(1.5)
    # pattern_manager.startPattern()

    # # Initialisation et lecture du signal
    # play_signal = PlaySignal(signal_synth, pattern_manager, activePorts, mappingIntensity)
    # play_signal.playSignal()