import numpy as np
import wave

def get_cepstrum(wav_file_name, sample_freq):
    spf = wave.open(wav_file_name,'r');
    fs = spf.getframerate();
    signal = spf.readframes(-1);
    signal = np.fromstring(signal, 'int16');

    """Computes cepstrum."""
    frame_size = signal.size
    #For normalization (/ tapering) the signal
    windowed_signal = np.hamming(frame_size) * signal
    #Sample Space
    dt = 1/sample_freq
    # Frequency Bins - Discrete Fourier Transform sample frequencies 
    # returns Array of length n//2 + 1 containing the sample frequencies.
    freq_vector = np.fft.rfftfreq(frame_size, d=dt)
    # Compute the one-dimensional discrete Fourier Transform for real input 
    X = np.fft.rfft(windowed_signal)
    # Log of FFT removing the negative
    log_X = np.log(np.abs(X))
    # FFT(LOG of FFT)
    cepstrum = np.fft.rfft(log_X)
    #resolution -- to check
    df = freq_vector[1] - freq_vector[0]
    # Sample Frequency for Log(FFT) 
    quefrency_vector = np.fft.rfftfreq(log_X.size, df)
    return quefrency_vector, cepstrum

# Detect fundamental frequency
def cepstrum_f0_detection(wav_file_in, sample_freq, fmin=82, fmax=640):
    """Returns f0 based on cepstral processing."""
    quefrency_vector, cepstrum = get_cepstrum(wav_file_in, sample_freq)
    # extract peak in cepstrum in valid region for guitar notes
    valid = (quefrency_vector > 1/fmax) & (quefrency_vector <= 1/fmin)
    max_quefrency_index = np.argmax(np.abs(cepstrum)[valid])
    f0 = 1/quefrency_vector[valid][max_quefrency_index]
    #print(quefrency_vector[valid])
    return f0 


print("frequency of A: ",cepstrum_f0_detection("A_open_tuner.wav",44100))
print("frequency of B: ",cepstrum_f0_detection("B_open_tuner.wav",44100))
print("frequency of D: ",cepstrum_f0_detection("D_open_tuner.wav",44100))
print("frequency of E1: ",cepstrum_f0_detection("E_open_1.wav",44100))
print("frequency of E6: ",cepstrum_f0_detection("E_open_up.wav",44100))
print("frequency of G: ",cepstrum_f0_detection("G_open_tuner.wav",44100))