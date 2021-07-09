#!/usr/bin/python3

"""
 RoboVision
 ______________

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

 Project Author/Architect: Navjot Singh <weavebytes@gmail.com>

"""

#
# face detection from an image using Haar cascade classifier
#

import numpy as np
import cv2 as cv
import pickle

from logger import get_logger
log = get_logger()


class FaceRecognition:

    def __init__(self, face_cascade_xml, eye_cascade_xml):


        # train/initialize face classifier
        face_cascade = cv.CascadeClassifier(face_cascade_xml)

        # train/initialize eye classifier
        eye_cascade = cv.CascadeClassifier(eye_cascade_xml)

        # creating a face recognier with pretrained data
        log.info("creating recognier from pre-trained data")
        recognizer = cv.face.LBPHFaceRecognizer_create() 
        recognizer.read("dataset/face_trainer.yml")

        # reading data from webcam
        # for internal webcam on laptop use 0
        # for external webcam on laptop/PC use 1
        cap = cv.VideoCapture(0)

        labels = {}

        font = cv.FONT_HERSHEY_SIMPLEX

        # load trained labels
        with open("dataset/face_trainer_labels.pickle", 'rb') as f:
            org_labels = pickle.load(f)
            labels = {v:k for k,v in org_labels.items()}

        log.info("capturing video data")
        while True:

            ret, img = cap.read()

            # HAAR cascade will need a grayscaled image to detect faces and eyes
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

            # lets find faces in the image and get their positions
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:

                # drawing rect for face
                cv.rectangle(img,(x,y),(x+w,y+h),(255, 0, 0), 2)

                # define roi for eyes detection,ideally, we should detect
                # eyes within the rectangular bounds of a face
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]

                # identify the face with recognizer
                index, conf = recognizer.predict(roi_gray)

                if conf > 75 and conf <= 95:
                    name = labels[index]
                    # Hurray, we detected a face !!!
                    print("Identified face: Name: %s, index: %d, confidence level: %d" % (name, index, conf))
                    cv.putText(img, name, (x,y), font, 1, (255,255,255), 1, cv.LINE_AA)

                # drawing rects for eyes
                eyes = eye_cascade.detectMultiScale(roi_gray)
                for (ex,ey,ew,eh) in eyes:
                    cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            cv.putText(img,'Press Esc to quit', (10, 450), font, 1, (255, 255, 255), 1, cv.LINE_AA)

            # showing image
            cv.imshow('Haar Face Detection', img)

            # wait for key for 10 mscs, or continue
            k = cv.waitKey(10) & 0xff

            # if 'esc' pressed, terminate
            if k == 27:
                break

        cap.release()
        cv.destroyAllWindows()

if __name__ == "__main__":

    # lets use pretrained cascade classifiers of opencv for face and eyes detection

    # path to Haar face classfier's xml file
    face_cascade_xml = './cascades/haarcascades_cuda/haarcascade_frontalface_default.xml'

    # path to Haar eye classfier's xml file
    eye_cascade_xml = './cascades/haarcascades_cuda/haarcascade_eye.xml'

    # run the eye detector with given classfiers
    fr = FaceRecognition(face_cascade_xml, eye_cascade_xml)

