import React from "react";

export default class ImageFromFolder extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            folder: "",
            images: ""
        }

        this.get_random_images = this.get_random_images.bind(this)
    }

    get_random_images() {
        fetch("http://localhost:8080/folder/out").then(data => data.json())
        .then(data => {
            console.log(data)
            this.setState({images: data})
        })
    }

    render() {
        return (
            <div>
                <div className="header">
                    <h1>Images from folder</h1>
                </div>
                <p style={{paddingTop: 100}}>The images will be taken from the data/images folder</p>
                <h3>Preview</h3>
                <button onClick={this.get_random_images}>Change pictures</button>
                <br />
                <div style={{marginTop: 25}}>
                    {this.state.images && this.state.images.map(i => <img src={i} style={{height: 150, margin: 10}} />)}
                </div>
            </div>
        )
    }
}