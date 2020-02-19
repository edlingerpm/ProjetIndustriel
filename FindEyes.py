import cv2
#import operator
import os
 
##############################################################################
#création d'un répertoire + nommage du fichier final
cheminImage = "./Images/"
try:
    # Bloc à essayer
    os.mkdir(cheminImage)
except:
    # Bloc qui sera exécuté en cas d'erreur
#    print("Le répertoire existe déjà")
    None  
    
nom = cheminImage+'images_Yeux.jpg'
###############################################################################

# create a new cam object
cap = cv2.VideoCapture(1)
# initialize the eyes recognizer (default face haar cascade)
face_cascade = cv2.CascadeClassifier("./haarcascade_eye.xml")
while True:
    # read the image from the cam
    ret, frame = cap.read()
    # converting to grayscale
    image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detect all the eyes in the image
    
    #faces = face_cascade.detectMultiScale(image_gray, 1.3, 5)
    faces = face_cascade.detectMultiScale(image_gray, 3, 5)
    
    print(str(len(faces)))
    
    # for every eye, draw a blue rectangle
    for x, y, width, height in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), color=(255, 0, 0), thickness=2)
    cv2.imshow("image", frame)
    
    #On quitte lorsque la touche "q" est pressée
    if cv2.waitKey(1) == ord("q"):
        break
    
cap.release()
cv2.destroyAllWindows()