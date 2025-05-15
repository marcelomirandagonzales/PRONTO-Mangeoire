import sounddevice as sd
import numpy as np
import soundfile as sf
from collections import deque
from datetime import datetime
from scipy.signal import butter, lfilter
import os
import time
import RPi.GPIO as GPIO
from subprocess import call

# --- Paramètres audio ---
RATE = 44100
CHANNELS = 2
THRESHOLD = -70.0  # Ajuste ce seuil selon tes tests
duration_before = 15  # secondes avant événement
duration_after = 15   # secondes après l'événement

# --- Buffers ---
buffer = deque(maxlen=int(RATE * duration_before))
intensity_buffer = deque(maxlen=int(RATE * 5))  # Buffer intensité pour 5 secondes

# -- Directory --
direct = '/home/Pronto/Recordings/'

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
    
#Paramètres ultrason
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define GPIO to use on Pi
GPIO_TRIGGER = 23
GPIO_ECHO    = 24



# Set pins as output and input
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

#Skipper photo
k=0

# --- Lancement du stream audio ---
with sd.InputStream(samplerate=RATE, channels=1, callback=audio_callback, blocksize=1024):
    print("Début de l'écoute en continu. Appuyez sur Ctrl+C pour arrêter.")
    try:
        while True:
            sd.sleep(1000)  # actualisation chaque seconde

            # --- Analyse d'intensité ---
            current_window = highpass_filter(np.array(intensity_buffer), cutoff=3000.0, fs=RATE)

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
                file_path = os.path.join(direct,filename)
                save_wav(file_path, filtered_audio, RATE)

                buffer.clear()
                intensity_buffer.clear()
                print("Écoute relancée...")
                
            time.sleep(0.5)

            # Send 10us pulse to trigger
            GPIO.output(GPIO_TRIGGER, True)
            time.sleep(0.00001)
            GPIO.output(GPIO_TRIGGER, False)
            start = time.time()

            while GPIO.input(GPIO_ECHO)==0:
              start = time.time()

            while GPIO.input(GPIO_ECHO)==1:
                stop = time.time()

            # Calculate pulse length
            elapsed = stop-start

            # Distance pulse travelled in that time is time
            # multiplied by the speed of sound (cm/s)
            distancet = elapsed * 34300

            # That was the distance there and back so halve the value
            distance = distancet / 2

            print ("Distance :", distance)
            if distance <= 15 and k==0 :
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                file_path = f"/home/Pronto/Photos/captured_{timestamp}.jpg"
                call(["libcamera-jpeg","--width", "1280","--height","720","-o",file_path])
                k=30
            elif k>0:
                k=k-1

    except KeyboardInterrupt:
        print("Arrêt de l'écoute.")


