import React from "react";
import logo from './logo.svg';
import './App.scss';

import ModulePipeline from "./components/box"
import TwitterModule from './modules/twitter/twitter';

import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import NSFW from './modules/nsfw/nsfw';
import ImageFromFolder from './modules/image_folder/images';
import MemeFilter from './modules/meme/meme';
import VisualizerService from './modules/visu/visu';
import Flood from "./modules/flood/flood";
import PrivatePublic from "./modules/private_public/private_public";

const getItems = (count, offset = 0) =>
    Array.from({ length: count }, (v, k) => k).map(k => ({
        id: `item-${k + offset}`,
        content: `item ${k + offset}`
    }));

// a little function to help us with reordering the result
const reorder = (list, startIndex, endIndex) => {
  const result = Array.from(list);
  const [removed] = result.splice(startIndex, 1);
  result.splice(endIndex, 0, removed);

  return result;
};

/**
* Moves an item from one list to another list.
*/
const move = (source, destination, droppableSource, droppableDestination) => {
  const sourceClone = Array.from(source);
  const destClone = Array.from(destination);
  const [removed] = sourceClone.splice(droppableSource.index, 1);

  destClone.splice(droppableDestination.index, 0, removed);

  const result = {};
  result[droppableSource.droppableId] = sourceClone;
  result[droppableDestination.droppableId] = destClone;

  return result;
};


export default class App extends React.Component {
  constructor(props) {
    super(props)

    this.dragEnd = this.dragEnd.bind(this)

    this.state = {
      current_editing: "",
      items: [],
      selected: [],
      ready: false
    }

    this.id2List = {
      droppable: 'items',
      droppable2: 'selected'
    };
  }

  componentDidMount() {
    fetch("http://localhost:8080/pipeline").then(data => data.json())
    .then(data => {
      let data_final = data.map((v, i) => ({content: v["name"], id: `item-${i}`, service_id: v["id"]}))
      console.log(data_final)
      this.setState({items: data_final, ready: true})
    })
  }

  getList = id => this.state[this.id2List[id]];

  updatePipeline(data) {
    let body = JSON.parse(JSON.stringify(data))
    fetch("http://localhost:8080/update", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body)
    }).then(data => console.log(data))
  }

  dragEnd(result) {
    console.log(result)
    const { source, destination } = result;

    // dropped outside the list
    if (!destination) {
        return;
    }

    if (source.droppableId === destination.droppableId) {
        const items = reorder(
            this.getList(source.droppableId),
            source.index,
            destination.index
        );

        let state = { items };

        if (source.droppableId === 'droppable2') {
            state = { selected: items };

            console.log("items couocu", items)
            this.updatePipeline(items)
        }

        this.setState(state);
    } else {
        const result = move(
            this.getList(source.droppableId),
            this.getList(destination.droppableId),
            source,
            destination
        );

        console.log("items coucou", result.droppable2)
        this.updatePipeline(result.droppable2)

        this.setState({
            items: result.droppable,
            selected: result.droppable2
        });
    }
  }

  render() {
    if (this.state.ready) {
      return (
        <div className="main">
          <div className="right">
            <div style={{display: this.state.current_editing == "Twitter crawler" ? "inline" : "none"}}>
              <TwitterModule />
            </div>
            <div style={{display: this.state.current_editing == "NSFW Network" ? "inline" : "none"}}>
              <NSFW />
            </div>
            <div style={{display: this.state.current_editing == "Images from folder" ? "inline" : "none"}}>
              <ImageFromFolder />
            </div>
            <div style={{display: this.state.current_editing == "Meme Filter" ? "inline" : "none"}}>
              <MemeFilter />
            </div>
            <div style={{display: this.state.current_editing == "Flood Filter" ? "inline" : "none"}}>
                <Flood />
            </div>
            <div style={{display: this.state.current_editing == "Visualizer" ? "inline" : "none"}}>
              <VisualizerService />
            </div>
            <div style={{display: this.state.current_editing == "Private Public" ? "inline" : "none"}}>
              <PrivatePublic />
            </div>
          </div>
          <div className="left">
            <div className="header">
                <h1>
                    Pipeline modules
                </h1>
            </div>
            <DragDropContext onDragEnd={this.dragEnd}>
                <Droppable droppableId="droppable">
                    {(provided, snapshot) => (
                        <div
                            ref={provided.innerRef}
                            className="list"
                        >
                            <h3>Available modules</h3>
                            {this.state.items.map((item, index) => (
                                <Draggable
                                    key={item.id}
                                    draggableId={item.id}
                                    index={index}>
                                    {(provided, snapshot) => (
                                        <div
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            className="box"
                                            >
                                            {item.content}
                                        </div>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
                <Droppable droppableId="droppable2">
                    {(provided, snapshot) => (
                        <div
                            ref={provided.innerRef}
                            className="list"
                        >
                            <h3>Pipeline</h3>
                            {this.state.selected.map((item, index) => (
                                <Draggable
                                key={item.id}
                                draggableId={item.id}
                                index={index}>
                                    {(provided, snapshot) => (
                                      <div
                                            onClick={() => {this.setState({current_editing: item.content})}}
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            className="box"    
                                        >
                                            {item.content}
                                        </div>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
            </DragDropContext>
  
          </div>
        </div>
      );
    } else {
      return <p>loading</p>
    }
  }
}
