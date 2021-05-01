from service import Service
from os import listdir
from os.path import isfile, join

class FolderService(Service):
    def get_images(self):
        images = [f for f in listdir(self.IMAGE_FOLDER) if isfile(join(self.IMAGE_FOLDER, f))]
        return images
