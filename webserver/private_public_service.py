import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F
import os
from PIL import Image
from service import Service

PRIVATE_SCENES = ['balcony', 'bathroom', 'beach_house', 'bedroom', 'car_interior', 'chalet', 'clean_room', 'close',
                  'computer_room',
                  'corridor', 'conference_room', 'dining_room', 'dressing_room', 'elevator_shaft', 'entrance_hall',
                  'home_office',
                  'hotel_room', 'house', 'jacuzzi', 'kitchen', 'laundromat', 'living_room', 'mansion',
                  'manufactured_home', 'mezzanine',
                  'nursery', 'office', 'patio', 'playroom', 'porch', 'recreation_room', 'sauna', 'shed', 'shower',
                  'storage_room',
                  'television_room', 'throne_room', 'tree_house', 'underwater', 'utility_room']

class PrivatePublicService(Service):

    def run(self, images):
        self.send("Launching the PP model", type="info")
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

        self.send("PP model finished", type="info")

    def setup(self):
        # th architecture to use
        arch = 'resnet18'

        # load the pre-trained weights
        model_file = '%s_places365.pth.tar' % arch
        if not os.access(model_file, os.W_OK):
            weight_url = 'http://places2.csail.mit.edu/models_places365/' + model_file
            os.system('wget ' + weight_url)

        self.model = models.__dict__[arch](num_classes=365)
        checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
        state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
        self.model.load_state_dict(state_dict)
        self.model.eval()

        # load the image transformer
        self.centre_crop = trn.Compose([
                trn.Resize((256,256)),
                trn.CenterCrop(224),
                trn.ToTensor(),
                trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        # load the class label
        file_name = 'categories_places365.txt'
        if not os.access(file_name, os.W_OK):
            synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt'
            os.system('wget ' + synset_url)
        self.classes = list()


        with open(file_name) as class_file:
            for line in class_file:
                self.classes.append(line.strip().split(' ')[0][3:])
        self.classes = tuple(self.classes)


    def classify(self, pil_image):
        input_img = V(self.centre_crop(pil_image).unsqueeze(0))
        logit = self.model.forward(input_img)
        h_x = F.softmax(logit, 1).data.squeeze()
        probs, idx = h_x.sort(0, True)


        return self.is_public(probs, idx)

    def is_public(self, probs, idx):
        res = 0
        tot = 0
        for i in range(5):
            if (self.classes[idx[i]] in PRIVATE_SCENES):
                res += probs[i]
            tot += probs[i]

        ratio = res / tot
        if (ratio < 0.5):
            return True, ratio, self.classes[idx[0]]

        return False, ratio, self.classes[idx[0]]


#%%

