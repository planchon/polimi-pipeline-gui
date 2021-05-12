# Polimi GUI Pipeline
A simple web user interface tool to interact with the crowds4svg project.

## How to use it ?

### Install the dependencies
#### Front-end (`site` folder)
The front runs on React and WebSockets. These are the only two "big" librairies used.
```
npm install <- install all the NodeJS depedencies
npm start   
```

#### Back-end (`webserver` folder)
The back run on : Flask, Websockets, Pandas, SQLlite3, Keras and Tensorflow, **PyTorch and Torchvision**.
```
pip3 install flask pandas flask_socketio flask_cors keras tensorflow sqlite3
```

### Install the dependencies
Download the weight for the differents neural networks.
 - `vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5` from polimi pipeline
 - `ImgMemeWeights.h5` from polimi pipeline
 - `flood-model` tmp from https://drive.google.com/file/d/1iPaDsYYcvIj0FUAgFZ0kJ1JxC-wI3bAr/view?usp=sharing

put them in the `data/models` folder.

pipeline link : https://gitlab.iiia.csic.es/crowd4sdg/polimipipeline/

### get your twitter credentials
you need twitter credentials in order to run the pipeline

## Contributing
### Project structure
```
    site <- front end stuff
    | src/modules    <- all the differents modules code
    | src/components <- components code
    | src/App.js     <- Main app code
    webserver <- back end stuff
    | utils/         <- utilities stuff
    | service.py     <- Service class defined here
    | ***_service.py <- Differents services
    | main.py        <- Webserver / Websocket python file
    | pipeline.py    <- Pipeline class defined here
```

### Project architecture
```
+-----------------+  +------------------+  +-------------------+
|     SQLLite     |  |  data/images/    |  |   Twitter API     |
+-----------------+  +------------------+  +-------------------+
       |  ^                |  ^                   |  ^
       v  |                v  |                   v  |
+--------------------------------------------------------------+
| +--------+         +--------+         +--------+             |
| | Module | <-sql-> | Module | <-sql-> | Module |  PIPELINE   |
| +--------+         +--------+         +--------+             |
+----^  |---------------^  |-----------------------------------+
     |  | ws            |  | ws             ^  | REST API
     |  v               |  v                |  v
+--------------------------------------------------------------+
|                   REACT FRONT SERVER                         |
+--------------------------------------------------------------+
```

The front server speak with the back server with :
 - REST API when speaking about the pipeline and to setup service
 - Websocket for running the service and getting real time data

### Backend : Service Class
Notable functions:
 - `set_room(room)` join a websockets room
 - `send(message, type)` send a message to the front end module (throught websocket)
 - `add_accepted_images(data)` add images to database, send them to front. Only images accepted by the network
 - `get_images` get the images return by the service
 - `run` make the module classify

## Authors:
 - Paul Planchon (FR/ERASMUS) : project architecture & design
