from service import Service
import keras
import numpy as np
from keras.applications import VGG19
from keras.models import Sequential
from keras.layers import Flatten, Dense, Activation
import tensorflow
from tensorflow.keras.applications.xception import preprocess_input
from PIL import Image
import json
import tensorflow as tf

class FloodService(Service):
    def run(self, images):
        self.send("Launching the Flood model", type="info")
        res = []
        tmp = []
        for img in images:
            pil_image = Image.open(self.IMAGE_FOLDER + "/" + img)
            print(img)
            if pil_image.format == "PNG":
                continue
            result = self.classify(pil_image)
            iid = img
            data = {
                "image": iid,
                "result": str(result[0]),
                "proba": str(result[1])
            }
            res.append(data)

            if result[0]:
                tmp.append(data)

            if len(tmp) == 5:
                self.add_accepted_images(tmp)
                tmp = []

            self.send("Image {} processed: result {}, proba: {}".format(iid, result[0], result[1]))

        self.send("Flood model finished", type="info")

    def setup(self):
        xception = tf.keras.applications.Xception(include_top=False,
                                                  weights='imagenet',
                                                  input_shape=(512, 512, 3))

        xception.trainable = False

        model = tf.keras.Sequential()
        model.add(xception)
        model.add(tf.keras.layers.GlobalAveragePooling2D())
        model.add(tf.keras.layers.Dense(units=2, activation='softmax'))
        self.model = model
        self.model.load_weights('data/models/wg/may5')


    def classify(self, pil_image):
        pil_image = pil_image.resize((512, 512))
        img_array = np.array(pil_image)
        img_array = np.expand_dims(img_array, 0)
        img_array = preprocess_input(img_array)

        predictions = self.model.predict(img_array)[0]
        is_flood = predictions[0]
        not_flood = predictions[1]

        return is_flood > 0.7, is_flood, None
