import React from "react";

export default class ModulePipeline extends React.Component {
    constructor(props) {
        super(props)
        this.name = props.name;
    }

    render() {
        return (
            <div className="box" onClick={() => this.props.onClick()}>
                {this.name}
            </div>
        )
    }
}