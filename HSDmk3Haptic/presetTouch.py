class ParamTouch:
    def __init__(self, signal, modulation, freq, amp, duration, pattern, speed, numRoundTrip=1):
        self.signal = signal
        self.modulation = modulation
        self.freq = freq
        self.amp = amp
        self.duration = duration
        self.pattern = pattern
        self.speed = speed
        self.numRoundTrip = numRoundTrip

class PresetsTouch:
    def __init__(self):
        self.Carresse1 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/CalmFMOD.wav",  # Signal audio
            modulation="Fade In/Out",  # Modulation appliquée
            freq=50.0,  # Fréquence en Hz
            amp=75,  # Amplitude (0-100)
            duration=1.978,  # Durée en secondes
            pattern="DroiteGauche",  # Type de pattern
            speed=1.0,  # Vitesse du pattern
            numRoundTrip=2  
        )
        
        self.Carresse2 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/ForestFMOD.wav",
            modulation="Aucune",
            freq=50.0,
            amp=133,
            duration=3.0,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=4
        )
        
        self.Carresse3 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/WaterWavesFMOD.wav",
            modulation="Aucune",
            freq=50.0,
            amp=50,
            duration=2.0,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=2
        )

        self.Carresse4 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/StrokingFMOD.wav",
            modulation="Fade In/Out",
            freq=50.0,
            amp=80,
            duration=1.978,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=2
        )

        self.Carresse5 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/ASMRstrokeFMOD.wav",
            modulation="Aucune",
            freq=50.0,
            amp=50,
            duration=3.0,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=4
        )   

        self.Carresse6 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/ASMRstrokeFastFMOD.wav",
            modulation="Aucune",
            freq=50.0,
            amp=40,
            duration=2.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=7
        )

        self.Carresse7 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/ShortStrokesFMOD.wav",
            modulation="Fade In/Out",
            freq=50.0,
            amp=100,
            duration=1.978,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=3
        )

        self.Carresse8 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/ShortStrokesEditFMOD.wav",
            modulation="Aucune",
            freq=50.0,
            amp=170.0,
            duration=3.0,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=4
        )

        self.CarresseTest = ParamTouch(
            signal="D:/Users/bdukatar/Documents/FMOD/test/Assets/testasstet/synthetic_vibration.wav",
            modulation="Aucune",
            freq=50.0,
            amp=2,
            duration=1.978,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=1
        )

        self.Frottement1 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/Frot/CatBrushFMOD.wav",
            modulation="Aucune",
            freq=250.0,
            amp=30,
            duration=3.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=6
            )
        
        self.Frottement2 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/Frot/BrushCreamFMOD.wav",
            modulation="Aucune",
            freq=250.0,
            amp=140,
            duration=3.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=5
            )
        
        self.Frottement3 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/Frot/WWindFMOD.wav",
            modulation="Aucune",
            freq=250.0,
            amp=20,
            duration=3.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=3
            )
        
        self.Frottement4 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/Frot/RubbingFMOD.wav",
            modulation="Aucune",
            freq=250.0,
            amp=100,
            duration=3.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=6
            )
        
        self.Frottement5 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/Frot/BetterScratchFMOD.wav",
            modulation="Aucune",
            freq=250.0,
            amp=50,
            duration=3.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=8
            )
        
        self.Frottement6 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/Frot/ASMRrubFMOD.wav",
            modulation="Aucune",
            freq=250.0,
            amp=75,
            duration=3.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=5
            )
        
        self.Frottement7 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/Frot/VeryStrokesFMOD.wav",
            modulation="Aucune",
            freq=250.0,
            amp=50.0,
            duration=4.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=5
            )
        
        self.Frottement8 = ParamTouch(
            signal="Bruit Blanc",
            modulation="Fade In/Out",
            freq=250.0,
            amp=0.20,
            duration=4.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=5
            )
        
        self.Tapotement1 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/glassTapFMOD.wav", 
            modulation="Aucune", 
            freq=150.0, 
            amp=8.0, 
            duration=0.5,
            pattern=None, 
            speed=1
        )
        
        self.Tapotement2 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/MultiTapFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=4.5, 
            duration=0.5,
            pattern=None, 
            speed=1
        )
        
        self.Tapotement3 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/TappingFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=4, 
            duration=0.5,
            pattern=None, 
            speed=1
        )
        
        self.Tapotement4 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/dTapPopFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=85, 
            duration=0.5,
            pattern=None, 
            speed=1
        )
        
        self.Tapotement5 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/HeartBeatFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=1.10, 
            duration=0.5,
            pattern=None, 
            speed=1
        )
        
        self.Tapotement6 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/ToyStuffAnimalFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=3, 
            duration=0.5,
            pattern=None, 
            speed=1
        )
        
        self.Tapotement7 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/ASMRtap2FMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=12.5, 
            duration=0.5,
            pattern=None, 
            speed=1
        )
        
        self.Frappe1 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/HitFMOD.wav", 
            modulation="Aucune", 
            freq=150.0, 
            amp=5, 
            duration=0.4,
            pattern=None, 
            speed=1
        )

        self.Frappe2 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/HittingFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=8,
            duration=0.26,
            pattern=None, 
            speed=1
        )

        self.Frappe3 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/TapFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=7,
            duration=0.28,
            pattern=None, 
            speed=1
        )
        
        self.Frappe4 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/clapMetalFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=125,
            duration=0.28,
            pattern=None, 
            speed=1
        )
        
        self.Frappe5 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/ASMRclapFMOD.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=8,
            duration=0.28,
            pattern=None, 
            speed=1
        )

        self.CaresseExpe1 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/EXPE/CareMeta.wav",
            modulation="Aucune",
            freq=50.0,
            amp=75,
            duration=1.978,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=2
        )

        self.CaresseExpe2 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/EXPE/CareAT.wav",
            modulation="Aucune",
            freq=20.0,
            amp=65,
            duration=1.978,
            pattern="DroiteGauche",
            speed=1.0,
            numRoundTrip=2
        )

        self.FrottementExpe1 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/EXPE/FrotMeta.wav",
            modulation="Aucune",
            freq=250.0,
            amp=30,
            duration=3.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=2
        )

        self.FrottementExpe2 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Caresse/Haptic/EXPE/FrotAT.wav",
            modulation="Aucune",
            freq=250.0,
            amp=65,
            duration=3.0,
            pattern="Horizontal",
            speed=1.0,
            numRoundTrip=2
        )

        self.TapotementExpe1 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/EXPE/TapMeta.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=3.0, 
            duration=0.5,
            pattern=None, 
            speed=1
        )

        self.TapotementExpe2 = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/EXPE/TapAT.wav",
            modulation="Aucune", 
            freq=150.0, 
            amp=2.5, 
            duration=0.5,
            pattern=None, 
            speed=1
        )

        self.FrappeExpe = ParamTouch(
            signal="D:/Users/bdukatar/perso/STAGE_ANR_Match/Audio_Vibr/SoundDesign/Tapotement/HapticFMOD/EXPE/HitASMR.wav", 
            modulation="Aucune", 
            freq=150.0, 
            amp=5,
            duration=0.28,
            pattern=None, 
            speed=1
        )
        



