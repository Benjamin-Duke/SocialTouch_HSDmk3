import socket
import sys
sys.path.append('c:\\Users\\benja\\Desktop\\Stage_ANR_Match\\ScriptTest\\HSDmk3Haptic')
from patternManager import PatternManager
from signalSynth import SignalSynth
from playSignal import PlaySignal
from presetTouch import PresetsTouch
import time  # Importer le module pour gérer le temps

def start_server():
    pattern_manager = PatternManager()
    signal_synth = SignalSynth()
    presets = PresetsTouch()

    activePorts = [0, 1, 4, 5, 6, 7]
    mappingIntensity = {
            "I1": 1,  # I1 -> port2
            "I2": 5,  # I2 -> port8
            "I3": 0,  # I3 -> port1
            "I4": 4,  # I4 -> port7
            "I5": 3,  # I5 -> port6
            "I6": 2,  # I6 -> port5
        }

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5000))
    server.listen(1)
    print("En attente de connexion depuis Unity...")

    connection, address = server.accept()
    print(f"Connexion établie avec Unity: {address}")

    last_command = None  # Stocker la dernière commande reçue
    last_time = 0  # Stocker l'horodatage de la dernière commande
    cooldown = 2  # Temps minimum (en secondes) entre deux commandes identiques

    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break

            decodeData = data.decode('ascii').strip()  # Décoder et supprimer les espaces inutiles
            if ":" not in decodeData:
                print(f"Format de données invalide : {decodeData}")
                continue

            current_time = time.time()  # Obtenir l'horodatage actuel
            if decodeData == last_command and (current_time - last_time) < cooldown:
                print(f"Commande ignorée car elle est identique à la précédente : {decodeData}")
                continue

            last_command = decodeData  # Mettre à jour la dernière commande
            last_time = current_time  # Mettre à jour l'horodatage

            touchName, soundID = decodeData.split(":", 1)
            soundID = soundID.strip()  # Nettoyer l'ID du son

            # Associer les noms de chaînes aux presets
            # presetsDict = {
            #     "Caresse": {
            #         "0": presets.Carresse1,  # Preset pour soundID 0
            #         "1": presets.Carresse2,  # Preset pour soundID 1
            #         "2": presets.Carresse3,  # Preset pour soundID 2
            #         "3": presets.Carresse4,  # Preset pour soundID 3
            #         "4": presets.Carresse5,  # Preset pour soundID 4
            #         "5": presets.Carresse6,  # Preset pour soundID 5
            #         "6": presets.Carresse7,  # Preset pour soundID 6
            #         "7": presets.Carresse8,  # Preset pour soundID 7
            #         "8": presets.CarresseTest,  # Preset pour soundID 8
            #     },
            #     "Frottement": {
            #         "0": presets.Frottement1,  # Preset pour soundID 0
            #         "1": presets.Frottement2,  # Preset pour soundID 1
            #         "2": presets.Frottement3,  # Preset pour soundID 2
            #         "3": presets.Frottement4,  # Preset pour soundID 3
            #         "4": presets.Frottement5,  # Preset pour soundID 4
            #         "5": presets.Frottement6,  # Preset pour soundID 5
            #         "6": presets.Frottement7,  # Preset pour soundID 6
            #     },
            #     "Tapotement": {
            #         "0": presets.Tapotement1,  # Preset pour soundID 0
            #         "1": presets.Tapotement2,  # Preset pour soundID 1
            #         "2": presets.Tapotement3,  # Preset pour soundID 2
            #         "3": presets.Tapotement4,  # Preset pour soundID 3
            #         "4": presets.Tapotement5,  # Preset pour soundID 4
            #         "5": presets.Tapotement6,  # Preset pour soundID 5
            #         "6": presets.Tapotement7,  # Preset pour soundID 6
            #     },
            #     "Frappe": {
            #         "0": presets.Frappe1,  # Preset pour soundID 0
            #         "1": presets.Frappe2,  # Preset pour soundID 1
            #         "2": presets.Frappe3,  # Preset pour soundID 2
            #         "3": presets.Frappe4,  # Preset pour soundID 3
            #         "4": presets.Frappe5,  # Preset pour soundID 4
            #     },
            # }
            presetsDict = {
                "Caresse": {
                    "0": presets.CaresseExpe1,  # Preset pour soundID 0
                    "1": presets.CaresseExpe2  # Preset pour soundID 1
                },
                "Frottement": {
                    "0": presets.FrottementExpe1,  # Preset pour soundID 0
                    "1": presets.FrottementExpe2  # Preset pour soundID 1
                },
                "Tapotement": {
                    "0": presets.TapotementExpe1,  # Preset pour soundID 0
                    "1": presets.TapotementExpe2  # Preset pour soundID 1
                },
                "Frappe": {
                    "0": presets.FrappeExpe
                },
                
            }
            touchPresets = presetsDict.get(touchName)
            if touchPresets is None:
                print(f"Nom de preset inconnu : {touchName}")
                continue

            preset = touchPresets.get(soundID)
            if preset is None:
                print(f"ID de son inconnu pour le toucher {touchName} : {soundID}")
                continue

            print(f"Nom : {touchName}")
            print(f"Preset : {preset}")
            print(f"ID du son : {soundID}")
            signal_synth.configureSignalFromPreset(preset)
            pattern_manager.configurePatternFromPreset(preset)

            play_signal = PlaySignal(signal_synth, pattern_manager, activePorts, mappingIntensity)
            play_signal.playSignal()


    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        connection.close()
        server.close()
        print("Connexion fermée")

if __name__ == "__main__":   
    start_server()