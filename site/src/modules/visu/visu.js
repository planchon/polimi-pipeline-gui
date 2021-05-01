import React from "react";

export default class VisualizerService extends React.Component {
    constructor(props) {
        super(props)

        this.state = {

        }

        this.get_images = this.get_images.bind(this)
    }

    get_images() {
        fetch("http://localhost:8080/visu/in?size=20").then(data => data.json())
        .then(data => this.setState({in_image: data}))
    }

    render() {
        return (
            <div>
                <div className="header">
                    <h1>Visualizer</h1>
                </div>
                <h3 style={{paddingTop: 80}}>See all the images out of the module above</h3>
                <button onClick={this.get_images}>get images</button>
                <br />
                <div style={{marginTop: 25}}>
                    {this.state.in_image && this.state.in_image.map(i => <img src={i} style={{height: 150, margin: 10}} />)}
                </div>
            </div>
        )
    }
}