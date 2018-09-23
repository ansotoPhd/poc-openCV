import os
import pickle
from pathlib import Path

from traitlets import (Unicode, )
from traitlets.config import LoggingConfigurable
import face_recognition
import cv2
import base64

current_dir = os.path.dirname(__file__)
project_dir = os.path.join(current_dir, "../")


class OpencvService(LoggingConfigurable):

    encodings = Unicode("faces_db/faces_db.db", config=True)
    images_dir = Unicode("images", config=True)
    detection_method = Unicode("cnn", config=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # => DB of processed images and recognized faces
        self.images_dict = {}
        self.faces_dict = {}

        # => Encodings/images files
        self.faces_db = os.path.join(project_dir, str(self.encodings))
        self.images_dir = os.path.join(project_dir, self.images_dir)

        self.images_dict = {str(path): None for path in Path(self.images_dir).glob('*.jpg')}
        self.images_list = list(self.images_dict.keys())
        print(str(len(self.images_list)) + " images found.")

        print(self.images_list)
        print(self.images_dict)

        # => load the known faces and embeddings
        if Path(self.faces_db).exists():
            self.data = pickle.loads(open(str(self.encodings), "rb").read())
        else:
            self.data = {}

    def proccess_image(self, image_index, height, width, method=None):

        method = self.detection_method if not method else method
        assert method in ["cnn", "hog"], "Invalid detection method"

        # · Getting image path
        image_path = self.images_list[image_index]
        # · Getting opencv image
        image, image_rgb = self.get_open_cv_image(image_path)
        # · Getting image descriptor
        image_descriptor = self.images_dict[image_path]

        if not image_descriptor or method not in image_descriptor["bboxes"]:
            print("Initiating detection ..")
            print("Method: " + str(method))
            image_descriptor = {"bboxes": {}, 'encodings': {}}
            # · Face detector
            bboxes = self.detect_faces(image_rgb, method)
            image_descriptor["bboxes"][method] = bboxes
            # · Face embeddings
            encodings = face_recognition.face_encodings(image_rgb, bboxes)
            image_descriptor['encodings'][method] = encodings
            # · Face recognition
            names = [None] * len(bboxes)
            image_descriptor['names'] = names
            self.images_dict[image_path] = image_descriptor
        else:
            print("Using previous detection ..")
            bboxes = image_descriptor["bboxes"][method]
            encodings = image_descriptor['encodings'][method]
            names = image_descriptor['names']

        print("Processing final image...")
        image = self.draw_bboxes_and_names(image, bboxes, names)
        image = self.resize_image_keep_ratio(image, height, width)

        return self.encode_image(image), len(self.images_list), method

    def get_image(self, index):
        return self.images_list[index]

    def get_open_cv_image(self, image_path):
        image = cv2.imread(image_path)  # openCV BGR # dlib ordering (RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image, image_rgb

    def resize_image_keep_ratio(self, image, height, width, inter=cv2.INTER_AREA):

        ih, iw, _ = image.shape
        print("Image shape: " + str(ih) + "x" + str(iw))

        rh = height / float(ih)
        rw = width / float(iw)
        r = min(rh, rw)
        dim = (int(iw * r), int(ih * r))
        # resize the image
        resized = cv2.resize(image, dim, interpolation=inter)
        # return the resized image
        return resized

    def detect_faces(self, image, method):
        boxes = face_recognition.face_locations(image, model=method)
        return boxes

    def get_encodings(self, image, boxes):
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(image, boxes)
        return boxes, encodings

    def draw_bounding_boxes(self, image, bboxes):
        for (top, right, bottom, left) in bboxes:
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        return image

    def draw_bboxes_and_names(self, image, bboxes, names):
        for ((top, right, bottom, left), name) in zip(bboxes, names):
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            name = "????" if not name else name
            cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 0), 2)
        return image

    def encode_image_path(self, image_path):
        image = cv2.imread(image_path)
        retval, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer).decode()
        return jpg_as_text

    def encode_image(self, image):
        retval, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer).decode()
        return jpg_as_text

