from service import Service
import keras
import numpy as np
from keras.applications import VGG19
from keras.models import Sequential
from keras.layers import Flatten, Dense, Activation
from PIL import Image
import json

class MemeService(Service):
    def run(self, images):
        self.send("Launching the MEME model", type="info")
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

        self.send("MEME model finished", type="info")

    def setup(self):
        model_vgg19 = VGG19(include_top=False, weights='data/models/vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5' , input_shape=(150, 150, 3))
        # copy vgg19 layers into our model
        self.model = Sequential()
        for layer in model_vgg19.layers:
            self.model.add(layer)

        # freezing vgg19 layers (saving its original weights)
        for i in self.model.layers:
            i.trainable = False

        self.model.add(Flatten())
        self.model.add(Dense(10))
        self.model.add(Activation('relu'))
        self.model.add(Dense(2, activation='softmax'))

        self.model.load_weights('data/models/ImgMemeWeights.h5')

    def classify(self, pil_image):
        pil_image = pil_image.resize((150,150))
        img_array = np.array(pil_image)
        img_array = np.expand_dims(img_array, 0)
        img_array = img_array / 255.

        predictions = self.model.predict(img_array)[0]
        is_image = predictions[0]
        is_meme = predictions[1]


        # Returns true (prediction < 0.5 ) if image is not a Meme
        return is_image > is_meme, is_image, None
