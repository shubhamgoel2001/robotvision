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
# a trainer for faces, inorder to identify faces with names/labels
#
# reference
# https://www.youtube.com/watch?v=PmZ29Vta7Vc
#

import os
import numpy as np
from PIL import Image
import cv2 as cv
import pickle


from PyQt5.QtCore import QObject, pyqtSignal

from threading import Thread

from global_signals import g_emitter

from logger import get_logger
log = get_logger()


class FaceTrainer(QObject, Thread):

    # signal for emitting a frame captured from camera
    processing_image = pyqtSignal('QString', 'QString')
    face_training_finished = pyqtSignal()

    def __init__(self, face_cascade_xml, face_images_dataset_dir, parent=None):
        super().__init__(parent)

        self.face_cascade = cv.CascadeClassifier(face_cascade_xml)
        self.recognizer = cv.face.LBPHFaceRecognizer_create()

        self.face_images_dataset_dir = face_images_dataset_dir

    def run(self):

        y_labels = []
        x_train = []
        cur_id = 0
        label_ids = {}

        # fetching images from dataset for training
        for root, dirs, files in os.walk(self.face_images_dataset_dir):

            # FIXME - adding talkative settings in prefs !!!
            # if our robot it too talkative, emit this signal
            g_emitter().emit_signal_to_feed_mouth(
                    "checking %s" % os.path.basename(root))

            for file in files:
                # check file extension for image files
                extension = os.path.splitext(file)[1]
                if extension in [".jpg", ".jpeg", ".png"]:
                    full_path = os.path.join(root, file)
                    label = os.path.basename(root).replace(" ", "-").lower()

                    if label not in label_ids:
                        label_ids[label] = cur_id
                        cur_id += 1

                    img_id = label_ids[label]
                    log.debug(
                            "FaceTrainer :: %s - %s - %s"
                            % (str(label), str(img_id), str(full_path)))

                    self.processing_image.emit(label, full_path)

                    # convert image to grayscale
                    pil_image = Image.open(full_path).convert("L")

                    # convery grayscale image to numpy array
                    image_array = np.array(pil_image, "uint8")

                    faces = self.face_cascade.detectMultiScale(
                            image_array, 1.3, 5)

                    for (x, y, w, h) in faces:
                        # define roi for eyes detection,ideally,
                        # we should detect eyes within the rectangular
                        # bounds of a face
                        roi = image_array[y:y+h, x:x+w]
                        x_train.append(roi)
                        y_labels.append(img_id)

        # save trained labels
        with open("dataset/face_trainer_labels.pickle", 'wb') as f:
            pickle.dump(label_ids, f)

        self.recognizer.train(x_train, np.array(y_labels))
        self.recognizer.save("dataset/face_trainer.yml")

        self.face_training_finished.emit()


if __name__ == "__main__":
    # path to Haar face classfier's xml file
    face_cascade_xml = './cascades/haarcascades_cuda/haarcascade_frontalface_default.xml'

    from local_settings import FACE_IMAGES_DATASET_DIR
    ft = FaceTrainer(face_cascade_xml, FACE_IMAGES_DATASET_DIR)
    ft.start()
    ft.join()
