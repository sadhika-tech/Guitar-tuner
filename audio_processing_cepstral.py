import numpy as np
from scipy.io.wavfile import write
import sounddevice as sd
import matplotlib.pyplot as plt
import customtkinter as ctk
import ceptstral_analysis_1 as cps1
import os

# Constants
wav_file = ""
min_string_freq = 82

deviation_range = 10
FREQUENCIES = {
    'E2': 82.41,
    'A2': 110.00,
    'D3': 146.83,
    'G3': 196.00,
    'B3': 246.94,
    'E4': 329.63,
}

def frequency_to_number(freq, a4_freq=440):
        """ converts a frequency to a note number (for example: A4 is 69)"""

        if freq == 0:
            sys.stderr.write("Error: No frequency data. Program has potentially no access to microphone\n")
            return 0

        note_freq1 = 12 * np.log2(freq / a4_freq) + 69
        print("Frequency to No", note_freq1 ) 
        return note_freq1

def number_to_frequency(number, a4_freq=440):
    """ converts a note number (A4 is 69) back to a frequency """

    return a4_freq * 2.0**((number - 69) / 12.0)

def save_audio_to_wavfile(audio, sample_rate):
    # Convert float64 audio data to int16 for WAV format
    audio_data_int16 = np.int16(audio * 32767)
    #To check this purpose
    if audio_data_int16.ndim == 1:  # If mono, reshape to 2D
        audio_data_int16 = audio_data_int16.reshape(-1, 1)

    # Save the recorded audio to a WAV file
    cwd = os.getcwd()
    wav_file1=os.path.join(cwd, "output.wav")
    write(wav_file1, sample_rate, audio_data_int16)
    print("Audio saved as output.wav")
    return wav_file1
    
def record_audio(duration, sample_rate, channels_in, dtype_in):
    global audio_signal    
    print("Recording...")
    frames=int(duration*sample_rate)
    # Record audio for the specified duration
    audio = sd.rec(frames, samplerate=sample_rate, channels=channels_in, dtype=dtype_in) 
    sd.wait()  # Wait until the recording is finished
    print("Recording finished.")
    #To Check
    if (channels_in == 1):
        audio.flatten()
        wav_file_tmp=""
    else : 
        #Write to Wav File
        wav_file_tmp = save_audio_to_wavfile(audio, sample_rate)
    return audio, wav_file_tmp

def find_deviation(stringfrequency_in, frequency_detected_in):
    #Postive Deviation
    if ( frequency_detected_in >= stringfrequency_in ):
        quotient = int(frequency_detected_in/stringfrequency_in)
        deviation =  frequency_detected_in - (stringfrequency_in*quotient)
        # check for freq difference from std freq / octaves is within the range
        if (int(deviation) >= deviation_range): 
            #Check for Deviation from higher octave
            deviation1 = ((stringfrequency_in*(quotient+1)) - frequency_detected_in)*-1
            if (int(abs(deviation1)) <= deviation_range):# Negative Deviation from Octave
                deviation = deviation1 # Negative Deviation from higher Octave
            else: #Check for the Lower Deviation and take it
                if (abs(deviation1) < deviation):
                    deviation = deviation1
        else:# Deviation less than Deviation Range
            pass
        print("Deviation :", deviation)                    
    else: #Frequency Detected is less than String Standard Frequency
        deviation1 =  (stringfrequency_in - frequency_detected_in) * -1
        # If Negative Deviation from Standard Frequency is within the range
        if (int(abs(deviation1)) <= deviation_range):
            deviation = deviation1 # Negative Deviation from Standard Frequency
        else: #Check for under tones within the 82 to 640 Range
            deviation = deviation1
            string_frequency_undertone = (stringfrequency_in/2)
            #If the Undertone > 82, then check for deviation otherwise retain the calculated deviation
            if (string_frequency_undertone > 82):
                deviation2 = find_deviation(string_frequency_undertone, frequency_detected_in)
                if (int(abs(deviation2)) <= deviation_range):
                    deviation = deviation2
    print(deviation)
    return deviation    

#To find the deviation between standard and received frequency
def find_deviation_old(stringfrequency_in, frequency_detected_in):
  
    quotient = int(frequency_detected_in/stringfrequency_in)
    if (quotient == 0):
        deviation = stringfrequency_in - frequency_detected_in
        if (abs(deviation) > deviation_range): # check for freq difference for octaves in the +/- 4 range
            if (abs(frequency_detected_in - stringfrequency_in)) <= deviation_range:
                deviation = abs(frequency_detected_in - stringfrequency_in)
            else:
                if (abs((frequency_detected_in*(quotient+1))- stringfrequency_in) <= deviation_range):
                    deviation = abs((frequency_detected_in*(quotient+1)) - stringfrequency_in)
    else:
        deviation =  frequency_detected_in - (stringfrequency_in*quotient)
        if (abs(deviation) > deviation_range): # check for freq difference for octaves in the +/- 4 range
            if (abs((stringfrequency_in*quotient) - frequency_detected_in) <= deviation_range):
                deviation = abs((stringfrequency_in*quotient) - frequency_detected_in)
            else:
                if (abs((stringfrequency_in*(quotient+1))- frequency_detected_in) <= deviation_range):
                    deviation = abs((stringfrequency_in*(quotient+1)) - frequency_detected_in)
    print(deviation)
    return deviation    
    

#CEPSTRAL Analysis
def find_deviation_ceps(wav_file_in, FreqSelected, sample_rate):
    fundamental_freq = cps1.cepstrum_f0_detection(wav_file_in, sample_rate)
    print('Standard Frequency : ', FreqSelected, 'Frequency Detected : ', fundamental_freq)
#    frequency_to_number(fundamental_freq)
    deviation = find_deviation(FreqSelected, fundamental_freq)
    print("Deviation ", deviation)
    # Calculate Deviation Percentage
    deviation_perc = int( (deviation/ FreqSelected)*100) 
    print("Deviation percentage ", deviation_perc)
    
    return_string = ""
    return_status = ""
    if (abs(deviation)) <= deviation_range:
        print("In Tune")
        return_status = "In Tune"
        return_string = "Deviation %:" + f"{deviation_perc:.2f}"
    else:
        print("Out of Tune")
        return_status = "Out of Tune"
        return_string = "Deviation %:" + f"{deviation_perc:.2f}"
    #If fundamental frequency is less than 60 Hz, do not display anything
    if (fundamental_freq < 60):
        return_status = "Skip"
        return_string = ""

    return deviation_perc, deviation, return_status, return_string 


