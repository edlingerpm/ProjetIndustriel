import cv2
import numpy as np
import os
import time
from datetime import datetime

TEMPSCOMMENCEMENT = 5
TEMPSATTENTE = 2

SURFACESIGNIFICATIVE = 15000

# 0 --> webcam
# 1 --> Nystagmus
# 2 --> Immobile
TYPEVIDEO = 0

#Ouverture de la camera principale, ici celle de l'ordinateur
if TYPEVIDEO == 0 :
    capture = cv2.VideoCapture(1)
else :
    if TYPEVIDEO == 1 :
        capture = cv2.VideoCapture("./Nystagmus2.mp4")
    else:
        if TYPEVIDEO == 3 :
            capture = cv2.VideoCapture("./ImmobileEyes.mp4")
        else:
            capture = cv2.VideoCapture("./DVD.mpg")

#Ou ouverture de la camera distante, ex le RaspeberryPi
#capture = cv2.VideoCapture('/dev/stdin')

#Aucune frame n'a encore été capturée, prevFrame est donc initialisé à None
prevFrame = None
premiereFrame = None
derniereFrame = None
i=1
j=1
Continuer = True
ComparaisonFaite = False
ABouge=False

now = datetime.now()

DerniereImageEnregistree = False

###############################################################################
#création d'un répertoire + nommage du fichier final
cheminImage = "./Images/"
try:
    # Bloc à essayer
    os.mkdir(cheminImage)
except:
    # Bloc qui sera exécuté en cas d'erreur
    #print("Le répertoire existe déjà")
    None  
###############################################################################

while True:
    (grabbed,frame) = capture.read()
    
    later = datetime.now()
    difference = (later - now).total_seconds()
    
    #Si la frame n'est pas lu correctement dans le buffer, on quitte la boucle
    if not grabbed:
        break
    
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(25,25), 0)
    
    # affichage du texte qui dit qu'il reste TEMPSCOMMENCEMENT secondes
    if difference <= TEMPSCOMMENCEMENT :
        cv2.putText(frame, "Start in "+ str(TEMPSCOMMENCEMENT-int(difference)) +" seconds",(20,20), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,255), 2, 1)
    else:
        #on garde en mémoire l'image
        #if prevFrame is None:
        #    prevFrame = gray
        
        #on garde en mémoire la 1ère image
        if premiereFrame is None:
            premiereFrame = gray
            #enregistrement de l'image
            ret, frame=capture.read()
            print("enregistrement 1ere image")
            cv2.imwrite(cheminImage+"1.jpg",frame)
            
        
        #print(str(int(difference)))
        
        #on garde en mémoire la dernière image
        if (int(difference) == TEMPSATTENTE+TEMPSCOMMENCEMENT)&(DerniereImageEnregistree==False):
            derniereFrame = gray
            ret, frame=capture.read()
            print("enregistrement dernière image")
            cv2.imwrite(cheminImage+"2.jpg",frame)
            DerniereImageEnregistree = True
            
        # lorsqu'on a dépassé le chrono
        if difference < TEMPSATTENTE+TEMPSCOMMENCEMENT:
            cv2.putText(frame, "Don't move. Still "+ str((TEMPSATTENTE+TEMPSCOMMENCEMENT)-int(difference)) +" seconds",(20,20), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,255), 2, 1)
    
    cv2.imshow('contour',frame)


    if prevFrame is None:
        prevFrame = gray

            
    if (DerniereImageEnregistree)&(ComparaisonFaite==False) :
        ComparaisonFaite=True
        #print("ICI")
    #On fait la difference absolue de l'image actuelle et la precedente
    #On fait un seuillage binaire sur cette nouvelle image
    #Puis on la dilate pour pouvoir plus facilement trouver les contours par la suite
    #    frameDelta = cv2.absdiff(prevFrame,gray)
        frameDelta = cv2.absdiff(premiereFrame,derniereFrame)
        thresh = cv2.threshold(frameDelta, 7, 255, cv2.THRESH_BINARY)[1]
        kernel = np.ones((11,11),np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=2)
    
        #Recherche des contours des objets de l'image dilate
        (img,contr,hrchy) = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
        #Ce mask va nous servir a encadrer l'objet de la couleur de celui ci
        mask = np.zeros(frame.shape[:2],np.uint8)

        for c in contr:
            #print(str(j))
            #j+=1
            #Tous les petits objets sont ignorés avec cette ligne
            if cv2.contourArea(c) < SURFACESIGNIFICATIVE:
                continue
            if cv2.contourArea(c) >= SURFACESIGNIFICATIVE:
                #åprint(">="+str(SURFACESIGNIFICATIVE))
                print("You moved.")
                ABouge=True
                
    #        print("assez grand" + str(i))
#            i+=1
            #Recherche des coordonnées de l'objet et on adapte le mask en fonction de l'objet
#            (x,y,w,h) = cv2.boundingRect(c) 
#            mask[y:y+h, x:x+w] = 255
    
            #Récuperation de la couleur du pixel du milieu
            #On suppose qu'on est dans le cas ou l'objet a une couleur uniforme
            """        (bl,gr,re) = frame[y+int((h/2)),x+int((w/2))]
            bl = int(bl) 
            gr = int(gr)
            re = int(re)
            couleur ='B:'+ str(bl) + 'G:' + str(gr) + 'R:' + str(re)
    
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame,couleur,(x+w,y), font, 1, (255,255,255), 2, cv2.LINE_AA)
            """
            #Le rectangle prend la couleur de l'objet et les nuances de bleu,vert,rouge sont affiche sur le cote
            # cv2.rectangle(frame,(x,y),(x+w,y+h),(bl,gr,re),3)
#            cv2.rectangle(frame,(x,y),(x+w,y+h),(0, 255, 0),3)
        
#            masked_img = cv2.bitwise_and(frame,frame,mask=mask)    
            
        if (ABouge==False):
            print("You did'nt moved.")
            
        #print("Fin Contr")
    #On affiche la video avec les rectangles
    cv2.imshow('contour',frame)
    

    #Les autres video (seuillage,masque...) pour tests
    #cv2.imshow('blur',gray)
    #cv2.imshow('res',frameDelta)
    #cv2.imshow('mask',masked_img)
    #cv2.imshow('res',thresh)

    #l'image actuelle devient la future image precedente
    prevFrame = gray

    #Quitte la capture video lorsque la touche q est appuyée
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()