import numpy as np
import matplotlib.pyplot as plt
import librosa
from scipy import signal
from math import sqrt
import os
import glob
import random
#import pandas as pd
T_extract = 3 #extrait de 3 secondes
New_Fs = 16000
N = 16000*6
F_range = np.linspace(0, New_Fs, N)
fmin = 80
fmax = 120
index_min = int(fmin * N / New_Fs)
index_max = int(fmax * N / New_Fs)

thresh = 13
dist = 15
def resample(audio_path,target_Fs):
    #original_extract = np.audioread(audio_path)
    #new_extract = np.random.randint(0,4096/2,14000*3)+2048
    audio_file, sr = librosa.load(audio_path)
    #resample at 14kHz
    downsampled_audio = librosa.resample(audio_file, orig_sr = sr, target_sr=target_Fs)
    new_extract = np.array(downsampled_audio)
   #print(new_extract)

    # Define the anti-aliasing filter
    nyquist_freq = New_Fs / 2
    cutoff_freq = 6500
    filter_order = 4
    b, a = signal.butter(filter_order, cutoff_freq/nyquist_freq, btype='lowpass')

    # Apply the filter to the signal
    #new_signal = signal.filtfilt(b, a, new_extract)
    t,n = getTandN(new_extract, New_Fs)
    if (n==3*New_Fs):
        return new_extract
    else : 
        return np.array([-1])

def even_extract(extract):
    #copy and mirror
    reversed_extract = np.copy(extract)
    reversedL = []
    for i in range(np.size(reversed_extract)):
        reversedL.append(reversed_extract[np.size(reversed_extract)-1-i])
    reversed_extract = np.array(reversedL)
    #concatenate the reversed extract with the original extract so that it is even => fft coef are all real
    new_data = np.append(extract,reversed_extract)
    return new_data

def getTandN(extract,Fs):
    T_extract = np.size(extract,0)/Fs
    N_sample = np.size(extract,0)
    return(T_extract,N_sample)

def markov(extract,Fs,twindow):
    #markov window
    window = np.zeros(np.size(extract,0))

    for i in range(0,New_Fs//10) : #fnetre de 0.1s
        window[i] = 10.0*i/New_Fs
        window[N_sample-i] = 10.0*i/New_Fs

    return extract*window

def process(audio_file):
    data = resample(audio_file, New_Fs)
    #print("enter :", data[0])
    if (data[0]==-1):
        return 0
    data = even_extract(data)
    T,N = getTandN(data,New_Fs)
    #print("T = ",T, "N = ",N)
    #fft
    FFT_extract = np.abs(np.fft.fft(data))
    FFT_extract[0]=0
    fftmax, fftmin = FFT_extract.max(), FFT_extract.min()
    FFT_extract = (FFT_extract - fftmin)*100/(fftmax - fftmin) 
    return FFT_extract[index_min-5:index_max+5]

def peak_detect(bee_zone,t,d,w):
    peaks = signal.find_peaks(bee_zone[5:-5],threshold=t,distance=d)
    plot_result(peaks, F_range, index_min, index_max, bee_zone)
    if (len(peaks[0]) > 0) :
        return "bee"
    else :
        return "nobee"
def peak_detect_show(bee_zone,t,d,w,):
    peaks = signal.find_peaks(bee_zone[5:-5],threshold=t,distance=d)
    plot_result(peaks, F_range, index_min, index_max, bee_zone)



def plot_result(peaks,F_range,index_min,index_max,bee_zone):
    plt.plot(F_range[index_min:index_max],bee_zone[5:-5],"r-")
    for i in peaks[0]:
        print(i,bee_zone[i-5:i+5],len(bee_zone))

        plt.plot(F_range[i-5+index_min:i+5+index_min],bee_zone[i:i+10],"go")
    plt.xscale("log")
    plt.xlim(10,10000)
    plt.show()
    print("done")


def get_wav_files(folder_path):
    """
    Returns a list of all WAV files in the specified folder
    """
    wav_files = []
    for file_path in glob.glob(os.path.join(folder_path, "*.wav")):
        if os.path.isfile(file_path):
            wav_files.append(file_path)
    print("nombre de fichier = ",len(wav_files))
    return wav_files


thresh_min = 10
thresh_max = 90
thresh_step = 3
dist_min = 3
dist_max = 30
dist_step = 3
width_min = 2
width_max = 20
width_step = 2
number_test = ((thresh_max - thresh_min)//thresh_step+1) * ((dist_max - dist_min)//dist_step+1) * ((width_max - width_min)//width_step)
print("Number of tests:", number_test)

confusion_matrix = [{"bee": {"bee": 0, "nobee": 0}, "nobee": {"bee": 0, "nobee": 0},"error" : 0, "threshold" : 0, "distance" : 0, "width" : 0}for i in range(number_test)]
wav_files = get_wav_files("./BDDextract")
sample_i_min = 0
sample_i_max = 3
samples = random.sample(wav_files,sample_i_max-sample_i_min)
#print("sample size : ", sample_i_max-sample_i_min)
file_c = 1
for audio_file in samples :
    c = 0
    fft = process(audio_file)
    #if (file_c % (len(samples)//10) == 0):
    #    print(file_c, "/",len(samples))
    file_c+=1
    if "nobee" in audio_file:
        expected_result = "nobee"
    else:
        expected_result = "bee"
    if (not isinstance(fft,int)) :
        for thresh in range(thresh_min,thresh_max,thresh_step):
            for dist in range(dist_min,dist_max,dist_step):
                for wi in range(width_min,width_max,width_step):
                    confusion_matrix[c]["distance"] = dist
                    confusion_matrix[c]["threshold"] = thresh
                    confusion_matrix[c]["width"] = wi
                    #wi = 1
                    actual_result = peak_detect(fft, thresh, dist, wi)
                    
                    if (actual_result == 0) :
                        confusion_matrix["error"]+=1
                        print("error in file : " + file_path)
                    else :
                        confusion_matrix[c][str(expected_result)][str(actual_result)] += 1
                    c+=1

#for i in confusion_matrix :
#    print(i)
def score() :
    score_max = -1.0
    best_param = confusion_matrix[1]
    for confusion in confusion_matrix :
        
        score_bee = confusion["bee"]["bee"]/(confusion["bee"]["bee"]+confusion["bee"]["nobee"]+1)
        score_nobee = confusion["nobee"]["nobee"]/(confusion["nobee"]["nobee"]+confusion["nobee"]["bee"]+1)
        if score_bee + score_nobee != 0 : 
            score_mean = 2 * ((score_bee * score_nobee) / (score_nobee + score_bee))
        else :
            score_mean = 0
        
        if score_mean > score_max :
            score_max = score_mean
            best_param = confusion
        print("threshold : ", confusion["threshold"], ", distance : ", confusion["distance"],"width", confusion["width"], ", score : ", score_bee, score_nobee, score_mean)
    print(best_param, ", score : ", score_max)
    #peak_detect_show(fft, best_param["threshold"], best_param["distance"], best_param["width"])
score()
