import React from "react";
import socketIOClient from "socket.io-client";

export default class PrivatePublic extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            in_image: [],
            console_message: [],
        }

        this.get_comming_image = this.get_comming_image.bind(this)
        this.run_model = this.run_model.bind(this)
    }

    get_comming_image() {
        fetch("http://localhost:8080/pp/in").then(data => data.json())
        .then(data => this.setState({in_image: data}))
    }

    run_model() {
        fetch("http://localhost:8080/socket").then(data => data.json())
        .then(data => {
            let socket = socketIOClient("http://localhost:8080")
            socket.emit("join", {room: data["socket"], service: "pp"})
            socket.on("message", data => {
                console.log("MESSAGE", data)
                switch (data["type"]) {
                    case 'tweet':
                        this.setState({tweets: JSON.parse(data["message"])})
                        break
                    case "image":
                        this.setState({images: JSON.parse(data["message"])})
                        break
                    default:
                        let mess = this.state.console_message
                        mess.push(data)
                        this.setState({console_message: mess})
                        break
                }
            })
        })
    }

    render() {
        return (
            <div>
                <div className="header">
                    <h1>ppFilter</h1>
                </div>

                <h3 style={{paddingTop: 75}}>Input data</h3>
                <p>Get a look at the data comming to the network</p>
                <button onClick={this.get_comming_image}>get images</button>
                <br />
                <div style={{marginTop: 25}}>
                    {this.state.in_image && this.state.in_image.map(i => <img src={i} style={{height: 150, margin: 10}} />)}
                </div>

                <h3>Run the model</h3>
                <p>If you think that the images comming are you, you can run the model</p>
                <button onClick={this.run_model}>Run the model</button>

                <h3>Console</h3>

                <div className="console">
                    {this.state.console_message.reverse().map(m => {
                        if (m["type"] == "error") {
                            return <p style={{color: "red"}}>{m["message"]}</p>
                        }
                        if (m["type"] == "info") {
                            return <p style={{color: "green"}}>{m["message"]}</p>
                        }
                        return <p>{m["message"]}</p>
                    })}
                </div>

                <h4>Results images</h4>
                {this.state.images && this.state.images.map(image => <img src={image}/>)}
            </div>
        )
    }
}