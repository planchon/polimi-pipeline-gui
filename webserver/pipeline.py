import json

class Pipeline:
    service_data = []
    service_available = []

    base_service = []

    def __init__(self, service_active, service_available):
        self.service_available = service_available
        self.base_service = service_available

    def process_service(self, service):
        pass

    def change_index_service(self, service, index):
        pass

    def get_service(self, service_name):
        all_serv = self.service_data + self.service_available
        for s in all_serv:
            if s.id == service_name:
                return s
        return None

    def get_all_service_json(self):
        all_service = self.base_service
        data = []
        for s in all_service:
            data.append({
                "name": s.name,
                "id": s.id,
            })

        return data

    def get_comming_images(self, service_id):
        index = self.get_index_service(service_id)
        images = self.service_data[index - 1].get_images()

        return images


    def get_index_service(self, service_id):
        index = 0
        for s in self.service_data:
            if s.id == service_id:
                return index
            index += 1

        return -1

    def run_service(self, service_id, room):
        serv = self.get_service(service_id)
        serv.set_room(room)
        images = self.get_comming_images(service_id)
        serv.run(images)


    def update(self, data):
        data = json.loads(data)
        self.service_available = self.base_service
        self.service_data = []
        for i in range(len(data)):
            serv = self.get_service(data[i]["service_id"])
            self.service_data.append(serv)

        print("----- NEW PIPELINE -----")
        print(self.service_data)