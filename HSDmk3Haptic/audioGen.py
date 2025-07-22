import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import butter, lfilter
import time
import threading
import math
import sys

# ============= CONSTANTES ET CONFIGURATION =============
SAMPLE_RATE = 48000  
DURATION = 2.0       # Durée du signal       
NUM_CHANNELS = 20    # Nombre de canaux du HSDmk3

# Ports actifs et leurs noms
ACTIVE_PORTS = [0, 1, 4, 5, 6, 7]  # Ports 1, 2, 5, 6, 7, 8 
PORT_NAMES = ['1', '2', '5', '6', '7', '8']  # Ports actifs

# Disposition pour l'interface (première ligne: 2,6,8, deuxième ligne: 1,5,7)
# 0=port1, 1=port2, 2=port5, 3=port6, 4=port7, 5=port8
PORT_LAYOUT = [[1, 3, 5], [0, 2, 4]]  # Layout: première ligne: 2,6,8, deuxième ligne: 1,5,7

# Correspondance entre intensités et ports
INTENSITY_TO_PORT_MAPPING = {
    "I1": 1,  # I1 -> port2
    "I2": 5,  # I2 -> port8
    "I3": 0,  # I3 -> port1
    "I4": 4,  # I4 -> port7
    "I5": 3,  # I5 -> port6
    "I6": 2,  # I6 -> port5
}

# Preset pour les paramètres de vibration
presets = {
    "Carresse": {
        "signal": "Sinusoïdal",
        "modulation": "Aucune",
        "freq": 50.0,
        "amp": 0.12,
        "pattern": "Horizontal",
        "delay": 0.07
    },
    "Frottement": {
        "signal": "Bruit Blanc",
        "modulation": "Aucune",
        "freq": 250.0,
        "amp": 0.12,
        "pattern": "DroiteGauche",
        "delay": 0.02
    },
    "Tapotemment": {
        "signal": "Tap",
        "modulation": "Aucune",
        "freq": 150.0,
        "amp": 0.08,
        "pattern": None,
        "delay": 0.02
    },
    "Frappe": {
        "signal": "Mixte",
        "modulation": "Impulsion",
        "freq": 150.0,
        "amp": 0.1,
        "pattern": None,
        "delay": 0.00
    },
}

# ============= VARIABLES GLOBALES =============
waveform = None        # Signal généré
stream = None          # Stream audio
is_playing = False     # Indique si le signal est en cours de lecture
buffer_position = 0    # Position actuelle dans le buffer audio
pattern_thread = None  # Thread pour les patterns de mouvement
pattern_running = False  # Indique si un pattern est en cours
current_pattern = None   # Pattern actuel

# Intensités individuelles pour chaque actionneur (valeurs initiales à 1.0)
port_intensities = {port: 1.0 for port in ACTIVE_PORTS}

# Liste pour stocker l'état de sélection des canaux
selected_channels = [False] * NUM_CHANNELS  # Par défaut, tous les canaux sont désactivés
for port in ACTIVE_PORTS:
    selected_channels[port] = True  # Activation des ports spécifiés

# ============= FONCTIONS AUDIO =============
def detect_audio_device():
    """Détecte les périphériques audio compatibles"""
    devices = sd.query_devices()
    device_list = {d["name"]: d["index"] for d in devices if d["max_output_channels"] == NUM_CHANNELS}
    
    if not device_list:
        print("Aucun périphérique avec 20 canaux trouvé.")
        return {}, ""
    
    print(f"Périphériques trouvés : {list(device_list.keys())}")
    default_device = list(device_list.keys())[0] if device_list else ""
    return device_list, default_device

def apply_preset(preset_name):
    """Applique les paramètres du preset sélectionné"""
    global pattern_running
    if preset_name not in presets:
        messagebox.showerror("Erreur", f"Preset '{preset_name}' non reconnu")
        return
    
    preset = presets[preset_name]
    
    # Appliquer les paramètres du preset
    signal_var.set(preset["signal"])
    mod_var.set(preset["modulation"])
    freq_var.set(preset["freq"])
    amp_var.set(preset["amp"])
    sleep_var.set(preset["delay"])
    
    # Mettre à jour les sliders et labels
    freq_label.config(text=f"Fréquence: {preset['freq']:.1f} Hz")
    amp_label.config(text=f"Amplitude: {preset['amp']:.2f}")
    sleep_label.config(text=f"Délai: {preset['delay']:.2f} s")
    
    # Mettre à jour le pattern actuel
    if pattern_running: stop_pattern()

    generate_signal()
    if preset["pattern"]:
        start_pattern(preset["pattern"])
    else:
        stop_pattern()
        reset_cursor_and_intensities()

from tkinter import filedialog  # Importer filedialog pour la sélection de fichiers
import wave  # Pour lire les fichiers audio WAV

def generate_signal(*args):
    """Génère le signal vibratoire selon les paramètres choisis"""
    global waveform
    freq = freq_var.get()
    amplitude = amp_var.get()
    signal_type = signal_var.get()
    modulation_type = mod_var.get()

    freq_label.config(text=f"Fréquence: {freq:.1f} Hz")
    amp_label.config(text=f"Amplitude: {amplitude:.2f}")

    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)

    if signal_type == "Sinusoïdal":
        waveform = amplitude * np.sin(2 * np.pi * freq * t)
    elif signal_type == "Bruit Blanc":
        waveform = amplitude * np.random.normal(0, 10, len(t))
        waveform = apply_lowpass_filter(waveform, freq, SAMPLE_RATE)
    elif signal_type == "Mixte":
        sine_wave = amplitude * np.sin(2 * np.pi * freq * t)
        noise = amplitude * np.random.normal(0, 2, len(t))
        noise = apply_lowpass_filter(noise, 500, SAMPLE_RATE)
        waveform = sine_wave + noise
    elif signal_type == "Train d'impulsion":
        interval = 0.05  # Intervalle entre les impulsions en secondes
        pulse_duration = 0.01  # Durée de chaque impulsion en secondes
        waveform = np.zeros_like(t)
        for i in range(len(t)):
            if (i / SAMPLE_RATE) % interval < pulse_duration:
                waveform[i] = amplitude*2
        waveform = svf_bandpass(waveform, SAMPLE_RATE, freq, q_factor=2)
    elif signal_type == "Triangulaire":
        waveform = amplitude * (2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1)
    elif signal_type == "Dente de Scie":
        waveform = amplitude * (2 * (t * freq - np.floor(t * freq + 0.5)))
    elif signal_type == "Tap":
        interval = 0.5  
        pulse_duration = 0.01  
        num_pulses = 3  
        pulse_spacing = 0.01  
        waveform = np.zeros_like(t)
        for i in range(len(t)):
            for j in range(num_pulses):
                if (i / SAMPLE_RATE) % interval < pulse_duration + j * pulse_spacing:
                    waveform[i] = amplitude
    elif signal_type == "Fichier Audio":
        # Ouvrir une boîte de dialogue pour sélectionner un fichier audio
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier audio",
            filetypes=[("Fichiers WAV", "*.wav"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            try:
                with wave.open(file_path, 'rb') as wav_file:
                    # Lire les données audio
                    num_frames = wav_file.getnframes()
                    audio_data = wav_file.readframes(num_frames)
                    audio_signal = np.frombuffer(audio_data, dtype=np.int16)
                    
                    # Normaliser et ajuster l'amplitude
                    waveform = amplitude * (audio_signal / np.max(np.abs(audio_signal)))
                    waveform = apply_lowpass_filter(waveform, 1000, SAMPLE_RATE)   
                    
                    # Ajuster la durée si nécessaire
                    if len(waveform) > len(t):
                        waveform = waveform[:len(t)]
                    elif len(waveform) < len(t):
                        waveform = np.pad(waveform, (0, len(t) - len(waveform)), 'constant')
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger le fichier audio : {e}")
                return

    waveform *= apply_modulation(t, modulation_type)

    plot_signal(t, waveform)

def apply_modulation(t, modulation_type):
    """Applique une modulation au signal selon le type choisi"""
    if modulation_type == "Aucune":
        return np.ones_like(t)
    elif modulation_type == "Sinusoïdale":
        return 0.5 * (1 - np.cos(2 * np.pi * 2 * t))
    elif modulation_type == "Exponentielle":
        return np.exp(-2 * t)  
    elif modulation_type == "Impulsion":
        attack_time = 0.01  
        decay_time = 0.05    
        mod_signal = np.zeros_like(t)
        mod_signal[t < attack_time] = t[t < attack_time] / attack_time
        mod_signal[(t >= attack_time) & (t < attack_time + decay_time)] = 1 - ((t[(t >= attack_time) & (t < attack_time + decay_time)] - attack_time) / decay_time)
        return mod_signal
    elif modulation_type == "Créneau":
        return 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 2 * t))
    elif modulation_type == "Logarithmique":
        return np.log(1 + 5 * t) / np.max(np.log(1 + 5 * t))
    elif modulation_type == "Fade In/Out":
        # Modulation de type fade in/out
        fade_in_time = 0.1  # Temps de fade in
        fade_out_time = 0.1  # Temps de fade out
        mod_signal = np.ones_like(t)
        fade_in = (t < fade_in_time)
        fade_out = (t > (t[-1] - fade_out_time))
        mod_signal[fade_in] = t[fade_in] / fade_in_time
        mod_signal[fade_out] = (t[-1] - t[fade_out]) / fade_out_time
        return mod_signal
    
    return np.ones_like(t)

def svf_bandpass(signal, sample_rate, center_freq, q_factor=1.0):
    # Initialisation des paramètres du filtre
    omega = 2 * np.pi * center_freq / sample_rate
    f = 2 * np.sin(omega) / q_factor   # Fréquence normalisée
    q = q_factor

    # États internes du filtre
    low, band = 0.0, 0.0
    output = np.zeros_like(signal)

    # Application du filtre passe-bande sur chaque échantillon
    for i, x in enumerate(signal):
        high = x - low - q * band
        band = f * high + band
        low = f * band + low
        output[i] = band  # Passe-bande

    return output

def apply_lowpass_filter(data, cutoff, fs, order=5):
    """Applique un filtre passe-bas au signal"""
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)


def plot_signal(t, waveform):
    """Affiche le signal et sa FFT"""
    ax.clear()
    ax.plot(t[:], waveform[:])
    ax.set_title("Signal Vibratoire")
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True)

    fft_vals = np.fft.rfft(waveform)
    fft_freq = np.fft.rfftfreq(len(waveform), 1 / SAMPLE_RATE)
    
    ax_fft.clear()
    #ax_fft.plot(fft_freq, 20 * np.log10(np.abs(fft_vals)))
    ax_fft.plot(fft_freq, np.abs(fft_vals))
    ax_fft.set_xlim(0, 400)
    ax_fft.set_title("FFT du Signal")
    ax_fft.set_xlabel("Fréquence (Hz)")
    ax_fft.set_ylabel("Amplitude (dB)")
    ax_fft.grid(True)

    canvas.draw()


def audio_callback(outdata, frames, time, status):
    """Callback pour le stream audio"""
    global waveform, buffer_position
    
    if status:
        print(f"Statut audio: {status}")
    
    if waveform is None:
        outdata.fill(0)
        return
    
    # Remplir le buffer avec le signal
    try:
        pos = buffer_position
        
        chunk = np.zeros((frames, NUM_CHANNELS))
        
        for port in ACTIVE_PORTS:
            if selected_channels[port]:
                end = min(pos + frames, len(waveform))
                n = end - pos
                
                chunk[:n, port] = waveform[pos:end] * port_intensities[port]
                
                if n < frames:
                    chunk[n:, port] = waveform[:frames-n] * port_intensities[port]
        
        outdata[:] = chunk
        
        buffer_position = (pos + frames) % len(waveform)
        
    # Gérer les erreurs d'index    
    except RuntimeError as e:
        print(f"Info: Initialisation du stream... ({e})")
        chunk = np.zeros((frames, NUM_CHANNELS))
        
        for port in ACTIVE_PORTS:
            if selected_channels[port]:
                end = min(frames, len(waveform))
                chunk[:end, port] = waveform[:end] * port_intensities[port]
        
        outdata[:] = chunk
        
        buffer_position = frames % len(waveform)


def play_signal(unity=False):
    """Joue le signal sur le HSDmk3"""
    global stream, is_playing, buffer_position
    
    if waveform is None:
        messagebox.showwarning("Attention", "Veuillez d'abord générer un signal")
        return
        
    if is_playing:
        stop_signal()
    
    if unity:
        device_list, default_device= detect_audio_device()
        print(f"Périphériques trouvés : {list(device_list.keys())}")
        device_name = default_device
    else:
        device_list, _= detect_audio_device() 
        device_name = selected_device.get()

    if not device_name:
        messagebox.showwarning("Attention", "Aucun périphérique audio sélectionné")
        return
        
    device_index = device_list[device_name]
    
    try:
        # Réinitialiser la position du buffer au début
        buffer_position = 0
        
        # Créer un stream avec callback pour faire jouer le son en continu
        stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            blocksize=2048,
            device=device_index,
            channels=NUM_CHANNELS,
            callback=audio_callback
        )
        
        # Démarrer le stream
        stream.start()
        time.sleep(0.1)
        
        is_playing = True
        
        update_play_button_states("disabled", "normal")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur de lecture : {e}")

def stop_signal():
    """Arrête la lecture du signal"""
    global stream, is_playing
    
    if stream is not None and stream.active:
        stream.stop()
        stream.close()
        stream = None
    
    is_playing = False

    update_play_button_states("normal", "disabled")


def update_play_button_states(play_state, stop_state):
    """Met à jour l'état des boutons de lecture/arrêt"""
    play_btn.config(state=play_state)
    stop_btn.config(state=stop_state)
    play_btn2.config(state=play_state)
    stop_btn2.config(state=stop_state)


# ============= FONCTIONS D'INTERFACE =============
def update_freq(value):
    """Met à jour la valeur de fréquence et le label correspondant"""
    freq_var.set(float(value))
    freq_label.config(text=f"Fréquence: {float(value):.1f} Hz")
    
def update_amp(value):
    """Met à jour la valeur d'amplitude et le label correspondant"""
    amp_var.set(float(value))
    amp_label.config(text=f"Amplitude: {float(value):.2f}")

def update_sleep_time(value):
    """Met à jour le temps de pause et le label correspondant"""
    sleep_var.set(float(value))
    sleep_label.config(text=f"Délai: {float(value):.2f} s")


def toggle_channel(channel_idx):
    """Active/désactive un canal"""
    selected_channels[ACTIVE_PORTS[channel_idx]] = not selected_channels[ACTIVE_PORTS[channel_idx]]
    update_port_visualization()


def get_I5I6(Iv, alpha, beta):
    """Calcule les intensités I5 et I6 (pour les actionneurs 6 et 5)"""
    if alpha > 0.5:
        I5 = 2 * Iv * (1 - alpha) * (1 - beta)
        I6 = 2 * Iv * (1 - alpha) * beta
    else:
        I5 = 2 * Iv * alpha * (1 - beta)
        I6 = 2 * Iv * alpha * beta
    return I5, I6


def update_intensities_from_position(x, y):
    """Met à jour les intensités des actionneurs en fonction de la position du curseur"""
    # Calculer les coordonnées du centre des cubes des ports 2, 1 et 8
    port2_center_x = actuator_canvas.coords(actuator_rects[0])[0] + actuator_size / 2
    port2_center_y = actuator_canvas.coords(actuator_rects[0])[1] + actuator_size / 2
    port1_center_x = actuator_canvas.coords(actuator_rects[3])[0] + actuator_size / 2
    port1_center_y = actuator_canvas.coords(actuator_rects[3])[1] + actuator_size / 2
    port8_center_x = actuator_canvas.coords(actuator_rects[2])[0] + actuator_size / 2
    port8_center_y = actuator_canvas.coords(actuator_rects[2])[1] + actuator_size / 2
    port6_center_x = actuator_canvas.coords(actuator_rects[1])[0] + actuator_size / 2
    port6_center_y = actuator_canvas.coords(actuator_rects[1])[1] + actuator_size / 2

    # Calculer les coordonnées normalisées alpha et beta
    beta = (y - port2_center_y) / (port1_center_y - port2_center_y)
    gamma = (x - port2_center_x) / (port8_center_x - port2_center_x)

    # S'assurer que les valeurs sont entre 0 et 1
    gamma = max(0, min(1, gamma))
    beta = max(0, min(1, beta))
    
    # Calculer les intensités pour chaque port
    Iv = 1  # Intensité de port Fantôme	
    if gamma < 0.5:
        alpha = (x - port2_center_x) / (port6_center_x - port2_center_x)
        I1 = (1 - alpha) * (1 - beta) * Iv
        I2 = 0
        I3 = (1-alpha) * beta * Iv
        I4 = 0
        I5 = alpha * (1 - beta) * Iv
        I6 = alpha * beta * Iv
    elif gamma > 0.5:
        alpha = (x - port6_center_x) / (port8_center_x - port6_center_x)
        I1 = 0
        I2 = alpha * (1 - beta) * Iv
        I3 = 0
        I4 = alpha * beta * Iv
        I5 = (1 - alpha) * (1 - beta) * Iv
        I6 = (1 - alpha) * beta * Iv
    elif gamma == 0.5:
        I1 = 0
        I2 = 0
        I3 = 0
        I4 = 0
        I5 = (1- beta) * Iv
        I6 = beta * Iv

    # I1 = (1 - alpha) * (1 - beta) * Iv  # Intensité I1 pour port2
    # I2 = alpha * (1 - beta) * Iv        # Intensité I2 pour port8
    # I3 = (1 - alpha) * beta * Iv        # Intensité I3 pour port1
    # I4 = alpha * beta * Iv              # Intensité I4 pour port7
    # I5, I6 = get_I5I6(Iv, alpha, beta)  # I5 pour port6, I6 pour port5
    
    # Limiter les intensités entre 0 et 1
    intensities = [max(min(x, 1), 0) for x in [I1, I2, I3, I4, I5, I6]]
    
    # Mettre à jour les intensités selon le mapping corrigé
    port_intensities[ACTIVE_PORTS[INTENSITY_TO_PORT_MAPPING["I1"]]] = intensities[0]  # I1 -> port2
    port_intensities[ACTIVE_PORTS[INTENSITY_TO_PORT_MAPPING["I2"]]] = intensities[1]  # I2 -> port8
    port_intensities[ACTIVE_PORTS[INTENSITY_TO_PORT_MAPPING["I3"]]] = intensities[2]  # I3 -> port1
    port_intensities[ACTIVE_PORTS[INTENSITY_TO_PORT_MAPPING["I4"]]] = intensities[3]  # I4 -> port7
    port_intensities[ACTIVE_PORTS[INTENSITY_TO_PORT_MAPPING["I5"]]] = intensities[4]  # I5 -> port6
    port_intensities[ACTIVE_PORTS[INTENSITY_TO_PORT_MAPPING["I6"]]] = intensities[5]  # I6 -> port5
    
    update_port_visualization()


def update_port_visualization():
    """Met à jour l'affichage visuel des ports et intensités"""
    for i in range(len(actuator_rects)):
        row = i // 3  
        col = i % 3   
        
        # Déterminer le port actuel (personnalisé ou par défaut)
        default_port_idx = PORT_LAYOUT[row][col]
        default_port = ACTIVE_PORTS[default_port_idx]
        actual_port = custom_port_mapping.get(i, default_port)
        
        # Trouver l'index du port dans ACTIVE_PORTS pour obtenir le nom
        port_position = ACTIVE_PORTS.index(actual_port)
        port_name = PORT_NAMES[port_position]
        
        # Obtenir l'intensité actuelle
        intensity = port_intensities.get(actual_port, 1.0)
        
        actuator_canvas.itemconfig(intensity_texts[i], text=f"Port {port_name}\n{intensity:.2f}")
        intensity_color = get_intensity_color(intensity)
        actuator_canvas.itemconfig(actuator_rects[i], fill=intensity_color)
    
def get_intensity_color(intensity):
    """Convertit une intensité en couleur (plus intense = plus foncé)"""
    # Convertir intensité (0-1) en composante RGB (255-0)
    intensity_scaled = int(255 * (1 - intensity))
    color = f'#{intensity_scaled:02x}{intensity_scaled:02x}ff'
    return color


def change_port_assignment(actuator_idx):
    """Ouvre une boîte de dialogue pour changer l'assignation de port"""
    def on_select():
        selected_port = int(port_var.get())
        custom_port_mapping[actuator_idx] = selected_port
        dialog.destroy()
        update_port_visualization()
        
    # Créer un dialogue
    dialog = tk.Toplevel(root)
    dialog.title(f"Changer l'assignation du port")
    dialog.geometry("300x200")
    dialog.resizable(False, False)
    dialog.transient(root)  # Rend le dialogue modal
    
    # Centre le dialogue sur l'écran principal
    dialog.geometry("+%d+%d" % (root.winfo_rootx() + 100, root.winfo_rooty() + 100))
    
    ttk.Label(dialog, text="Sélectionnez un nouveau port:", font=("Arial", 12)).pack(pady=10)
    
    # Boutons radio pour sélectionner le port
    port_var = tk.StringVar(value=str(custom_port_mapping.get(actuator_idx, ACTIVE_PORTS[PORT_LAYOUT[actuator_idx//3][actuator_idx%3]])))
    
    for port in ACTIVE_PORTS:
        ttk.Radiobutton(dialog, text=f"Port {PORT_NAMES[ACTIVE_PORTS.index(port)]}", 
                       variable=port_var, value=str(port)).pack(anchor=tk.W, padx=20, pady=5)
    
    ttk.Button(dialog, text="Appliquer", command=on_select).pack(pady=10)


def reset_cursor_and_intensities():
    """Réinitialise la position du curseur et les intensités des actionneurs"""
    # Replacer le curseur au centre
    actuator_canvas.coords(cursor_rect, cursor_start_x, cursor_start_y, 
                         cursor_start_x + cursor_size, cursor_start_y + cursor_size)
    
    # Réinitialiser toutes les intensités à 1.0
    for port in ACTIVE_PORTS:
        port_intensities[port] = 1.0
    
    # Réinitialiser la carte personnalisée des ports
    custom_port_mapping.clear()
    
    update_port_visualization()
    


def is_valid_cursor_area(x, y):
    """Vérifie si la position du curseur est valide"""
    return (matrix_start_x <= x <= matrix_start_x + matrix_width and 
            matrix_start_y <= y <= matrix_start_y + matrix_height)


def move_cursor_to(x, y):
    """Déplace le curseur à la position spécifiée"""
    # Limiter le mouvement du curseur à l'intérieur de la matrice
    new_x = max(matrix_start_x, min(x - cursor_size//2, matrix_start_x + matrix_width - cursor_size))
    new_y = max(matrix_start_y, min(y - cursor_size//2, matrix_start_y + matrix_height - cursor_size))
    
    # Mettre à jour la position du curseur
    actuator_canvas.coords(cursor_rect, new_x, new_y, new_x + cursor_size, new_y + cursor_size)
    
    # Mettre à jour les intensités en fonction de la nouvelle position
    update_intensities_from_position(new_x + cursor_size//2, new_y + cursor_size//2)


def on_mouse_down(event):
    """Gestion du clic de souris pour le déplacement du curseur"""
    global dragging
    stop_pattern()  
    
    if actuator_canvas.find_withtag(tk.CURRENT) or is_valid_cursor_area(event.x, event.y):
        dragging = True
        move_cursor_to(event.x, event.y)
        actuator_canvas.bind("<Motion>", on_mouse_move)


def on_mouse_up(event):
    """Gestion du relâchement du clic de souris"""
    global dragging
    dragging = False
    actuator_canvas.unbind("<Motion>")


def on_mouse_move(event):
    """Gestion du déplacement de la souris"""
    if dragging:
        move_cursor_to(event.x, event.y)


def on_closing():
    """Fermeture propre de l'application"""
    stop_pattern()  
    stop_signal()   
    
    # Arrêter tous les threads et processus en arrière-plan
    if pattern_thread and pattern_thread.is_alive():
        pattern_running = False
        pattern_thread.join(1)  
    
    if stream and stream.active:
        stream.stop()
        stream.close()
    
    root.destroy()  
    sys.exit()  


# ============= FONCTIONS POUR LES PATTERNS =============
def stop_pattern():
    """Arrête un pattern en cours"""
    global pattern_thread, pattern_running
    pattern_running = False
    if pattern_thread and pattern_thread.is_alive():
        pattern_thread.join(1)  
    pattern_thread = None
    pattern_label.config(text="Pattern: Aucun")


def circular_pattern():
    """Déplace le curseur en cercle"""
    global pattern_running
    pattern_running = True
    pattern_sleep_time = sleep_var.get()
    
    center_x = matrix_start_x + matrix_width / 2
    center_y = matrix_start_y + matrix_height / 2
    radius = min(matrix_width, matrix_height) / 3
    angle = 0
    
    while pattern_running:
        angle += 0.05
        if angle > 2 * math.pi:
            angle = 0
            
        x = center_x + radius * math.cos(angle) - cursor_size/2
        y = center_y + radius * math.sin(angle) - cursor_size/2
        
        root.after(0, lambda x=x, y=y: move_cursor_to(x + cursor_size/2, y + cursor_size/2))
        time.sleep(pattern_sleep_time)  # Contrôle de la vitesse


def zigzag_pattern():
    """Déplace le curseur en zigzag horizontal"""
    global pattern_running
    pattern_running = True
    pattern_sleep_time = sleep_var.get()
    
    min_x = matrix_start_x + cursor_size
    max_x = matrix_start_x + matrix_width - cursor_size
    steps = 20
    step_size = (max_x - min_x) / steps
    
    y_positions = [
        matrix_start_y + matrix_height / 4,
        matrix_start_y + (matrix_height * 3) / 4
    ]
    
    y_idx = 0
    direction = 1  # 1 = droite, -1 = gauche
    x = min_x
    
    while pattern_running:
        x += step_size * direction
        
        # Changer de direction aux bords
        if x >= max_x or x <= min_x:
            direction *= -1
            y_idx = (y_idx + 1) % len(y_positions)
        
        # Utiliser after pour mettre à jour l'UI depuis le thread principal
        root.after(0, lambda x=x, y=y_positions[y_idx]: 
                   move_cursor_to(x + cursor_size/2, y + cursor_size/2))
        time.sleep(pattern_sleep_time)  # Contrôle de la vitesse


def RL_pattern():
    """Déplace le curseur horizontalement de droite à gauche"""
    global pattern_running
    pattern_running = True
    patternSleepTime = sleep_var.get()
    
    min_x = matrix_start_x + cursor_size
    max_x = matrix_start_x + matrix_width - cursor_size
    y = matrix_start_y + matrix_height / 2 - cursor_size / 2

    print(max_x, min_x, max_x - min_x)
    
    while pattern_running:
        # Mouvement de droite à gauche
        for x in np.linspace(max_x, min_x, 20):
            if not pattern_running:
                break
            # Utiliser after pour mettre à jour l'UI depuis le thread principal
            root.after(0, lambda x=x, y=y: move_cursor_to(x + cursor_size/2, y + cursor_size/2))
            time.sleep(patternSleepTime)


def diagonal_pattern():
    """Déplace le curseur en diagonale"""
    global pattern_running
    pattern_running = True
    pattern_sleep_time = sleep_var.get()
    
    # Points diagonaux
    points = [
        (matrix_start_x + cursor_size, matrix_start_y + cursor_size),  # Coin supérieur gauche
        (matrix_start_x + matrix_width - cursor_size, matrix_start_y + matrix_height - cursor_size),  # Coin inférieur droit
        (matrix_start_x + cursor_size, matrix_start_y + matrix_height - cursor_size),  # Coin inférieur gauche
        (matrix_start_x + matrix_width - cursor_size, matrix_start_y + cursor_size),  # Coin supérieur droit
    ]
    
    current_point = 0
    steps_between_points = 30
    
    while pattern_running:
        start_point = points[current_point]
        next_point = points[(current_point + 1) % len(points)]
        
        for step in range(steps_between_points):
            if not pattern_running:
                break
                
            progress = step / steps_between_points
            x = start_point[0] + (next_point[0] - start_point[0]) * progress
            y = start_point[1] + (next_point[1] - start_point[1]) * progress
            
            # Utiliser after pour mettre à jour l'UI depuis le thread principal
            root.after(0, lambda x=x, y=y: move_cursor_to(x + cursor_size/2, y + cursor_size/2))
            time.sleep(pattern_sleep_time)  # Contrôle de la vitesse
        
        current_point = (current_point + 1) % len(points)


def horizon_pattern():
    """Déplace le curseur horizontalement de gauche à droite puis de droite à gauche"""
    global pattern_running
    pattern_running = True
    patternSleepTime = sleep_var.get()
    
    min_x = matrix_start_x + cursor_size
    max_x = matrix_start_x + matrix_width - cursor_size
    y = matrix_start_y + matrix_height / 2 - cursor_size / 2
    
    while pattern_running:
        # Mouvement de gauche à droite
        for x in np.linspace(min_x, max_x, 20):
            if not pattern_running:
                break
            # Utiliser after pour mettre à jour l'UI depuis le thread principal
            root.after(0, lambda x=x, y=y: move_cursor_to(x + cursor_size/2, y + cursor_size/2))
            time.sleep(patternSleepTime)
        
        # Mouvement de droite à gauche
        for x in np.linspace(max_x, min_x, 20):
            if not pattern_running:
                break
            # Utiliser after pour mettre à jour l'UI depuis le thread principal
            root.after(0, lambda x=x, y=y: move_cursor_to(x + cursor_size/2, y + cursor_size/2))
            time.sleep(patternSleepTime)
            
def vertical_pattern():
    """Déplace le curseur de haut en bas puis de bas en haut"""
    global pattern_running
    pattern_running = True
    patternSleepTime = sleep_var.get()
    
    min_y = matrix_start_y + cursor_size
    max_y = matrix_start_y + matrix_height - cursor_size
    x = matrix_start_x + matrix_width / 2 - cursor_size / 2
    
    while pattern_running:
        # Mouvement de haut en bas
        for y in np.linspace(min_y, max_y, 20):
            if not pattern_running:
                break
            # Utiliser after pour mettre à jour l'UI depuis le thread principal
            root.after(0, lambda x=x, y=y: move_cursor_to(x + cursor_size/2, y + cursor_size/2))
            time.sleep(patternSleepTime)
        
        # Mouvement de bas en haut
        for y in np.linspace(max_y, min_y, 20):
            if not pattern_running:
                break
            # Utiliser after pour mettre à jour l'UI depuis le thread principal
            root.after(0, lambda x=x, y=y: move_cursor_to(x + cursor_size/2, y + cursor_size/2))
            time.sleep(patternSleepTime)



def start_pattern(pattern_name):
    """Démarre un pattern de mouvement"""
    global pattern_thread, pattern_running, current_pattern
    
    # Arrêter tout pattern en cours
    stop_pattern()
    
    # Définir le nouveau pattern
    patterns = {
        "Circulaire": circular_pattern,
        "Zigzag": zigzag_pattern,
        "DroiteGauche": RL_pattern,
        "Diagonal": diagonal_pattern,
        "Horizontal": horizon_pattern,
        "Vertical": vertical_pattern
    }
    
    # Vérifier si le pattern existe
    if pattern_name not in patterns:
        messagebox.showerror("Erreur", f"Pattern '{pattern_name}' non reconnu")
        return
        
    # Mettre à jour le label de pattern actuel
    current_pattern = pattern_name
    pattern_label.config(text=f"Pattern: {pattern_name}")
    
    # Démarrer le thread du pattern
    pattern_running = True
    pattern_thread = threading.Thread(target=patterns[pattern_name])
    pattern_thread.daemon = True
    pattern_thread.start()
    
# ============= INTERFACE GRAPHIQUE =============
# Initialisation de la fenêtre principale
root = tk.Tk()
root.title("Contrôleur d'Actionneurs Vibrotactiles - HSDmk3")

root.geometry("1920x1080")
root.protocol("WM_DELETE_WINDOW", on_closing)  # Gestion de la fermeture propre de l'application

# Style pour les widgets
style = ttk.Style()
style.configure("TButton", font=("Arial", 12))
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
style.configure("TRadiobutton", font=("Arial", 11), background="#f0f0f0")

# Cadre principal (avec deux colonnes)
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# ---- Colonne gauche (contrôles) ----
left_frame = ttk.Frame(main_frame, padding="5")
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Cadre pour les périphériques audio
device_frame = ttk.LabelFrame(left_frame, text="Périphérique Audio", padding="10")
device_frame.pack(fill=tk.X, padx=5, pady=5)

# Détection des périphériques audio
device_list, default_device = detect_audio_device()
selected_device = tk.StringVar(value=default_device)

# Menu déroulant pour les périphériques audio
ttk.Label(device_frame, text="Sélectionner un périphérique:").pack(anchor=tk.W)
device_menu = ttk.Combobox(device_frame, textvariable=selected_device, state="readonly")
device_menu['values'] = list(device_list.keys())
device_menu.pack(fill=tk.X, pady=5)

# Cadre pour les presets
preset_frame = ttk.LabelFrame(left_frame, text="Presets", padding="10")
preset_frame.pack(fill=tk.X, padx=5, pady=5)

# Menu déroulant pour les presets
preset_var = tk.StringVar()
preset_menu = ttk.Combobox(preset_frame, textvariable=preset_var, values=list(presets.keys()), state="readonly")
preset_menu.pack(fill=tk.X, pady=5)

# Bouton pour appliquer le preset sélectionné
apply_preset_btn = ttk.Button(preset_frame, text="Appliquer Preset", command=lambda: apply_preset(preset_var.get()))
apply_preset_btn.pack(fill=tk.X, pady=5)


# Cadre pour les paramètres du signal
signal_frame = ttk.LabelFrame(left_frame, text="Paramètres du Signal", padding="10")
signal_frame.pack(fill=tk.X, padx=5, pady=5)

# Variables pour les paramètres du signal
freq_var = tk.DoubleVar(value=100.0)
amp_var = tk.DoubleVar(value=0.1)
signal_var = tk.StringVar(value="Sinusoïdal")
mod_var = tk.StringVar(value="Aucune")

# Sliders pour les paramètres
ttk.Label(signal_frame, text="Type de Signal:").pack(anchor=tk.W)
signal_types = ["Sinusoïdal", "Train d'impulsion", "Triangulaire", "Dente de Scie", "Bruit Blanc", "Mixte", "Tap","Fichier Audio"]
signal_menu = ttk.Combobox(signal_frame, textvariable=signal_var, values=signal_types, state="readonly")
signal_menu.pack(fill=tk.X, pady=5)

ttk.Label(signal_frame, text="Type de Modulation:").pack(anchor=tk.W)
modulation_types = ["Aucune", "Sinusoïdale", "Exponentielle", "Impulsion", "Créneau", "Logarithmique","Fade In/Out"]
mod_menu = ttk.Combobox(signal_frame, textvariable=mod_var, values=modulation_types, state="readonly")
mod_menu.pack(fill=tk.X, pady=5)

# Slider pour la fréquence
freq_label = ttk.Label(signal_frame, text=f"Fréquence: {freq_var.get():.1f} Hz")
freq_label.pack(anchor=tk.W, pady=(10, 0))
freq_slider = ttk.Scale(signal_frame, from_=1.0, to=500.0, variable=freq_var, command=update_freq)
freq_slider.pack(fill=tk.X, pady=5)
freq_slider.bind("<ButtonRelease-1>", generate_signal)

# Slider pour l'amplitude
amp_label = ttk.Label(signal_frame, text=f"Amplitude: {amp_var.get():.2f}")
amp_label.pack(anchor=tk.W, pady=(10, 0))
amp_slider = ttk.Scale(signal_frame, from_=0.0, to=0.5, variable=amp_var, command=update_amp)
amp_slider.pack(fill=tk.X, pady=5)
amp_slider.bind("<ButtonRelease-1>", generate_signal)

# Bouton pour générer le signal
generate_btn = ttk.Button(signal_frame, text="Générer le Signal", command=generate_signal)
generate_btn.pack(fill=tk.X, pady=10)

# Cadre pour la visualisation du signal (FFT et temporel)
plot_frame = ttk.LabelFrame(left_frame, text="Visualisation du Signal", padding="10")
plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Création de la figure pour matplotlib
fig = plt.figure(figsize=(6, 6), dpi=100)
ax = fig.add_subplot(211)  # Signal temporel
ax_fft = fig.add_subplot(212)  # FFT

# Intégration de matplotlib dans tkinter
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Boutons de contrôle (lecture/arrêt)
control_frame = ttk.Frame(left_frame, padding="10")
control_frame.pack(fill=tk.X, padx=5, pady=5)

play_btn = ttk.Button(control_frame, text="▶️ Lecture", command=play_signal)
play_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

stop_btn = ttk.Button(control_frame, text="⏹️ Arrêt", command=stop_signal, state="disabled")
stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

# ---- Colonne droite (actionneurs) ----
right_frame = ttk.Frame(main_frame, padding="5")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Cadre pour le contrôle spatial des actionneurs
actuator_frame = ttk.LabelFrame(right_frame, text="Contrôle Spatial des Actionneurs", padding="10")
actuator_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Canvas pour afficher les actionneurs et le curseur
actuator_canvas = tk.Canvas(actuator_frame, width=600, height=400, bg="white")
actuator_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Taille et positions pour la matrice 2x3
actuator_size = 80
spacing = 40

# Position de la matrice sur le canvas
matrix_start_x = 50
matrix_start_y = 50
matrix_width = 3 * actuator_size + 2 * spacing
matrix_height = 2 * actuator_size + spacing

# Variables pour le mapping personnalisé des ports
custom_port_mapping = {}

# Création des rectangles pour les actionneurs
actuator_rects = []
intensity_texts = []

for row in range(len(PORT_LAYOUT)):
    for col in range(len(PORT_LAYOUT[0])):
        x = matrix_start_x + col * (actuator_size + spacing)
        y = matrix_start_y + row * (actuator_size + spacing)
        
        # Index du port dans la matrice
        port_idx = PORT_LAYOUT[row][col]
        port = ACTIVE_PORTS[port_idx]
        
        # Créer le rectangle de l'actionneur
        rect = actuator_canvas.create_rectangle(x, y, x + actuator_size, y + actuator_size, 
                                               fill="gray", outline="black", width=2)
        actuator_rects.append(rect)
        
        # Ajouter le texte d'intensité et le port
        text = actuator_canvas.create_text(x + actuator_size/2, y + actuator_size/2, 
                                          text=f"Port {PORT_NAMES[port_idx]}\n1.00", 
                                          font=("Arial", 10), fill="black")
        intensity_texts.append(text)
        
        # Double-clic pour modifier l'assignation de port
        actuator_index = row * 3 + col
        actuator_canvas.tag_bind(rect, "<Double-Button-1>", 
                                lambda event, idx=actuator_index: change_port_assignment(idx))
# Cursor for positioning
cursor_size = 20
cursor_start_x = matrix_start_x + matrix_width / 2 - cursor_size / 2
cursor_start_y = matrix_start_y + matrix_height / 2 - cursor_size / 2
cursor_rect = actuator_canvas.create_rectangle(cursor_start_x, cursor_start_y, 
                                              cursor_start_x + cursor_size, cursor_start_y + cursor_size, 
                                              fill="red", outline="darkred", width=2)

# Cadre pour les patterns de mouvement
pattern_frame = ttk.LabelFrame(right_frame, text="Patterns de Mouvement", padding="10")
pattern_frame.pack(fill=tk.X, padx=5, pady=5)

# Slider pour le délai entre les étapes du pattern
sleep_var = tk.DoubleVar(value=0.02)
sleep_label = ttk.Label(pattern_frame, text=f"Délai: {sleep_var.get():.2f} s")
sleep_label.pack(anchor=tk.W)
sleep_slider = ttk.Scale(pattern_frame, from_=0.001, to=0.1, variable=sleep_var, command=update_sleep_time)
sleep_slider.pack(fill=tk.X, pady=5)

# Boutons pour les patterns
pattern_buttons_frame = ttk.Frame(pattern_frame)
pattern_buttons_frame.pack(fill=tk.X, pady=5)

patterns = ["Circulaire", "Zigzag", "DroiteGauche", "Diagonal", "Horizontal", "Vertical"]
for i, pattern in enumerate(patterns):
    btn = ttk.Button(pattern_buttons_frame, text=pattern, 
                    command=lambda p=pattern: start_pattern(p))
    btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky=tk.EW)

# Bouton pour arrêter le pattern
stop_pattern_btn = ttk.Button(pattern_frame, text="Arrêter le Pattern", command=stop_pattern)
stop_pattern_btn.pack(fill=tk.X, pady=10)

# Label pour afficher le pattern actuel
pattern_label = ttk.Label(pattern_frame, text="Pattern: Aucun")
pattern_label.pack(pady=5)

# Bouton pour réinitialiser la position du curseur et les intensités
reset_btn = ttk.Button(pattern_frame, text="Réinitialiser Position et Intensités", 
                       command=reset_cursor_and_intensities)
reset_btn.pack(fill=tk.X, pady=10)

# Cadre pour les contrôles supplémentaires
extra_frame = ttk.Frame(right_frame, padding="10")
extra_frame.pack(fill=tk.X, padx=5, pady=5)

# Boutons de lecture/arrêt supplémentaires
play_btn2 = ttk.Button(extra_frame, text="▶️ Lecture", command=play_signal)
play_btn2.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

stop_btn2 = ttk.Button(extra_frame, text="⏹️ Arrêt", command=stop_signal, state="disabled")
stop_btn2.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

# Configuration des événements de la souris pour déplacer le curseur
dragging = False
actuator_canvas.bind("<ButtonPress-1>", on_mouse_down)
actuator_canvas.bind("<ButtonRelease-1>", on_mouse_up)

# Mise à jour initiale de l'affichage
update_port_visualization()

# Démarrage de la boucle principale
if __name__ == "__main__":    
    # Génération initiale du signal
    generate_signal()
    
    # Démarrage de la boucle principale
    root.mainloop()