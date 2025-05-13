import sounddevice as sd
import numpy as np
import soundfile as sf
from collections import deque
from datetime import datetime
import time
import RPi.GPIO as GPIO
from subprocess import call

# Paramètres audio
RATE = 44100
CHANNELS = 2
THRESHOLD = 95.0  # Ajuste ce seuil selon tes tests

duration_before = 5  # secondes avant événement
duration_after = 5   # secondes après l'évènement

# Buffers
buffer = deque(maxlen=int(RATE * duration_before))
intensity_buffer = deque(maxlen=int(RATE * 5))  # Buffer intensité pour 5 secondes

# Fonction pour sauvegarder un fichier FLAC

def save_wav(filename, data, samplerate):
    filename = filename.replace('.wav', '.flac')
    sf.write(filename, data, samplerate, format='FLAC')
    print(f"Audio enregistré sous {filename}")


# Callback audio pour enregistrement continu
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

# Lancement du stream audio
with sd.InputStream(samplerate=RATE, channels=1, callback=audio_callback, blocksize=1024):
    print("Début de l'écoute en continu. Appuyez sur Ctrl+C pour arrêter.")
    try:
        while True:
            sd.sleep(1000)  # actualisation chaque seconde

            # Calculer la moyenne de l'intensité sonore des 5 dernières secondes
            if len(intensity_buffer) == RATE * 5:
                current_window = np.array(intensity_buffer)
                avg_intensity = np.max(np.abs(current_window)) * 100
                print(f"Intensité sonore (moyenne 5 sec): {avg_intensity:.2f}")

                intensity_buffer.clear()  # Réinitialiser chaque seconde pour une moyenne nette

                if avg_intensity > THRESHOLD:
                    print("Son détecté, enregistrement en cours...")

                    previous_audio = np.array(buffer)
                    next_audio = sd.rec(int(RATE * duration_after), samplerate=RATE, channels=1)
                    sd.wait()

                    combined_audio = np.concatenate((previous_audio, next_audio[:,0]))

                    filename = datetime.now().strftime("record_%Y%m%d_%H%M%S.wav")
                    save_wav(filename, combined_audio, RATE)

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
            if distance <= 5 and k==0 :
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                file_path = f"/home/Pronto/programmes2025/Photos/captured_{timestamp}.jpg"
                call(["libcamera-jpeg","--width", "1280","--height","720","-o",file_path])
                k=30
            elif k>0:
                k=k-1

    except KeyboardInterrupt:
        print("Arrêt de l'écoute.")

