import os
from pathlib import Path
from pydub import AudioSegment

#from pathlib import open

#####################################################################
#####################################################################
# A LANCER OBLIGATOIREMENT AU DEBUT DU PROGRAMME
# retourne le nom du disque sur lequel le programme travaille (C:/ ou D:/)
def Init(): #initialise les chemins
    home = Path.home()
    path_beg = home.parts[0]
    path_beg='D'+path_beg[1:]
    return path_beg
#####################################################################
#####################################################################


#####################################################################
#####################################################################
def list_files_by_ext(folder_path,suff):
#liste tous les fichiers ayant l'extension suff dans le dossier de chemin absolu folder_path
#retourne une liste de ces fichiers

    # Créer une liste vide pour stocker les noms de fichiers
    files = [] 
    files=list(folder_path.glob('**/*'+suff))
    return files
#####################################################################
#####################################################################


#####################################################################
#####################################################################
def delete_ext(files):
#supprime les extensions des chemins contenus dans la liste files
# C:/Bureau/MonCV.pdf devient C:/Bureau/MonCV
# Un fichier sans extension reste inchangé
        for i in range(len(files)):
                   files[i]=files[i].with_suffix("")
#####################################################################
#####################################################################


#####################################################################
#####################################################################
#add the suffix 'suff' at the end of the path
def add_ext(files,suff):
#ajoute l'extension suff a la fin de tous les chemins de la liste files
    for i in range(len(files)):
        files[i]=files[i].with_suffix(suff)
#####################################################################
#####################################################################

#####################################################################
#####################################################################
# Ouvrir le fichier texte d'intervalles et lire les intervalles ligne par ligne
def split_was_using_lab(audio_file_wav,interval_file_lab,save_path,lastID,min_interval_time=3,save_path_cut=False):
    sound = AudioSegment.from_wav(audio_file_wav)
    if not save_path_cut: save_path_cut=save_path # si pas de chemin specifie pour les enregistrements cut, alors ils sont ranges avec les normaux
    
    f= interval_file_lab.open()
    lines = f.readlines()
    
    min_interval_time_ms = min_interval_time * 1000
    
    for i, line in enumerate(lines):
        
        #gestion de l en tete du fichier texte et de ses donnees
        if (i==0):
            head_file=line.strip()
            #print(head_file)
        
        #gestion du reste du fichier texte
        elif (line!=".\n"):
            
            #extraction de chaque ligne 
            #une ligne contient le debut et la fin de l intervalle et le label associe
            start_time, end_time, label = map(str, line.strip().split("	",2))
            #print("extrait n",i," tdep=",start_time," tfin=",end_time," lbl=",label)
            
            # Conversion des temps de sec en msec
            start_time_ms = float(start_time) * 1000
            end_time_ms = float(end_time) * 1000
            
            
            # Calcul de la duree totale de l intervalle
            interval_duration_ms=end_time_ms-start_time_ms
            
            # Calcul du nombre de decoupage necessaire de l intervalle
            nb_interval_line=int((interval_duration_ms//min_interval_time_ms))
            # verification de la presence ou non d un intervalle supplementaire cut
            # i.e. de temps trop court (< min_interval_time)
            is_there_one_more_interval_cut = interval_duration_ms%min_interval_time_ms
            # is_there_one_more_interval_cut peut etre vu comme un booleen
            
            #on decoupe maintenant l'intervalle en sous intervalle de min_interval_time sec
            for u in range(nb_interval_line): #tous les extraits complets
                lastID+=1
                ID = lastID
                if (lastID < 10):
                    ID = "0000"+str(lastID)
                elif (lastID < 100):
                    ID = "000"+str(lastID)
                elif (lastID < 1000):
                    ID = "00"+str(lastID)
                elif (lastID < 10000):
                    ID = "0"+str(lastID)

                this_interval_start_ms = start_time_ms+u*min_interval_time_ms
                this_interval_end_ms = this_interval_start_ms+min_interval_time_ms
                
                # Extraire l'intervalle du fichier audio en utilisant PyDub
                interval = sound[this_interval_start_ms:this_interval_end_ms]
            
                # Définir le nom de fichier pour l'intervalle en utilisant l'index de ligne
                filename = Path(save_path,ID + "_" + label + ".wav")
                interval.export(filename, format="wav")
            
            #gestion de l eventuel intervalle coupe
            if (is_there_one_more_interval_cut):
                lastID+=1
                ID = lastID
                if (lastID < 10):
                    ID = "0000"+str(lastID)
                elif (lastID < 100):
                    ID = "000"+str(lastID)
                elif (lastID < 1000):
                    ID = "00"+str(lastID)
                elif (lastID < 10000):
                    ID = "0"+str(lastID)
                interval = sound[start_time_ms+nb_interval_line*min_interval_time_ms:end_time_ms]
                filename = Path(save_path_cut,ID + "_" + label + "_cut.wav")
                interval.export(filename, format="wav")
    return(lastID)
#####################################################################
#####################################################################

     
#Initialisation
beg = Init()

#####################################################################
####################### SECTION DES PARAMETRES ######################
#####################################################################
#chemin absolu de la BDD
#chemin = Path(beg,"Téléchargements","BDD_PIR") 
chemin = Path('./BDD_PIR') 

#extension des fichiers à rechercher (ici audio en .wav)
extension = ".wav" 

#on numerote a partir de 0
StartID=0

#on desire des intervalles de 3sec
dureeIntervalle=3 

SavePath=   Path("./BDDextract")                #chemin absolu ou seront enregistres les extraits assez longs
SavePathCut=   Path("./BDDextract_poubelle")             #chemin absolu ou seront enregistres les extraits poubelles, si 0, ils seront enregistrés avec les fichiers de taille correcte
#####################################################################
##################### FIN SECTION DES PARAMETRES ####################
#####################################################################


audio_files = list_files_by_ext(chemin,extension) #listage des fichiers audio
delete_ext(audio_files) #suppression des extensions afin de pouvoir rechercher leur fichiers texte associes
lab_files=audio_files[:] #creation de la liste des fichiers texte associes
add_ext(audio_files, ".wav") #ajout des extensions
add_ext(lab_files, ".lab") #ajout des extensions

for i in range(len(audio_files)):
    StartID=int(split_was_using_lab(audio_files[i],lab_files[i],SavePath,StartID,dureeIntervalle,SavePathCut))
    print(i+1,"/",len(audio_files)," - ",StartID, " audiofiles created")

        
#MEMO
# .suffix pour obtenir l'extension
# autom l'entree des chemins