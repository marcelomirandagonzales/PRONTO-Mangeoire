import sounddevice as sd
import numpy as np
import soundfile as sf
from collections import deque
from datetime import datetime
from scipy.signal import butter, lfilter

# --- Paramètres audio ---
RATE = 44100
CHANNELS = 2
THRESHOLD = -50.0  # Ajuste ce seuil selon tes tests
duration_before = 5  # secondes avant événement
duration_after = 5   # secondes après l'événement

# --- Buffers ---
buffer = deque(maxlen=int(RATE * duration_before))
intensity_buffer = deque(maxlen=int(RATE * 5))  # Buffer intensité pour 5 secondes

# --- Filtrage passe-haut Butterworth ---
def butter_highpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    return butter(order, normal_cutoff, btype='high', analog=False)

def highpass_filter(data, cutoff=1500.0, fs=44100, order=4):
    b, a = butter_highpass(cutoff, fs, order=order)
    return lfilter(b, a, data)

# --- Fonction pour sauvegarder un fichier FLAC ---
def save_wav(filename, data, samplerate):
    filename = filename.replace('.wav', '.flac')
    sf.write(filename, data, samplerate, format='FLAC')
    print(f"Audio enregistré sous {filename}")

# --- Fonction score ---
def score(x, threshold, axis=0):
    x = np.asarray(x)
    x = x >= threshold
    count = sum(x, axis)
    s = sum(x, axis) / x.shape[axis]
    return s, count

# --- Activité acoustique ---
def acoustic_activity(xdB, dB_threshold, axis=1):
    ACTfract, ACTcount = score(xdB, dB_threshold, axis=axis)
    ACTfract = ACTfract.tolist()
    ACTcount = ACTcount.tolist()
    ACTmean = dB2linear(xdB[xdB > dB_threshold], mode='power')
    return ACTfract, ACTcount, ACTmean

# --- Conversion dB vers linéaire ---
def dB2linear(x, mode='amplitude', db_gain=0):
    if mode == 'amplitude':
        y = 10**((x - db_gain) / 20)
    elif mode == 'power':
        y = 10**((x - db_gain) / 10)
    return y

# --- Callback pour audio continu ---
def audio_callback(indata, frames, time, status):
    global buffer, intensity_buffer
    buffer.extend(indata[:, 0])
    intensity_buffer.extend(indata[:, 0])

# --- Lancement du stream audio ---
with sd.InputStream(samplerate=RATE, channels=1, callback=audio_callback, blocksize=1024):
    print("Début de l'écoute en continu. Appuyez sur Ctrl+C pour arrêter.")
    try:
        while True:
            sd.sleep(1000)  # actualisation chaque seconde

            # --- Analyse d'intensité ---
            current_window = highpass_filter(np.array(intensity_buffer), cutoff=1500.0, fs=RATE)

            # --- Calcul de l'activité acoustique ---
            xdB = 10 * np.log10(np.abs(current_window) ** 2 + 1e-11)
            _, ACT, _ = acoustic_activity(xdB, dB_threshold=THRESHOLD + 12, axis=-1)
            ACT = np.sum(np.asarray(ACT)) / RATE
            print(f"Activité acoustique: {ACT:.2f}")

            intensity_buffer.clear()

            if ACT > 0.6:  # Seuil ajustable
                print("Son détecté, enregistrement en cours...")

                # --- Pré-enregistrement ---
                previous_audio = np.array(buffer)

                # --- Enregistrement post-détection ---
                next_audio = sd.rec(int(RATE * duration_after), samplerate=RATE, channels=1)
                sd.wait()

                combined_audio = np.concatenate((previous_audio, next_audio[:, 0]))

                # --- Filtrage de l'audio complet ---
                filtered_audio = highpass_filter(combined_audio, cutoff=1500.0, fs=RATE)

                # --- Sauvegarde ---
                filename = datetime.now().strftime("record_%Y%m%d_%H%M%S.wav")
                save_wav(filename, filtered_audio, RATE)

                buffer.clear()
                intensity_buffer.clear()
                print("Écoute relancée...")

    except KeyboardInterrupt:
        print("Arrêt de l'écoute.")


