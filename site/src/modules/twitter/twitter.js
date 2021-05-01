import React from "react";
import "./twitter.scss";
import socketIOClient from "socket.io-client";
import ReactJson from 'react-json-view'

import DatePicker from 'react-date-picker'

export default class TwitterModule extends React.Component {
    constructor(props) {
        super(props)

        this.set_keywords = this.set_keywords.bind(this)
        this.twitter_cred = this.twitter_cred.bind(this)

        this.state = {
            cons_key:"vrTd61KlXggKVgenyOp15Aool",
            cons_sec:"XHb2VFfpOCkL3lzNNiEhSPitZykHz5U3F0kGR9vHaKIFzwjpQR",
            acc_tok:"860610854311661568-WAObgkQHeQ8wr1uNdBHDTBmWzLX2W1I",
            acc_sec: "AGTYR5K8YjIs01PtibQOfH0GvibeZ1s3Sf6U5FYj4TX3X",
            cred_error: "missing auth & keywords",
            cred_succ: "",
            keyword: "obama",
            start_date: new Date("01/06/2021"),
            end_date: new Date(),
            socket: null,
            socket_on: false,
            console_message: [],
            tweets: []
        }
    }

    twitter_cred() {
        let data = {
            type: "creds",
            ... this.state
        }

        this.set_data(data, "Error in twitter auth", "Twitter credentials set")
    }

    set_data(data, error_text, success_text) {
        fetch("http://localhost:8080/twitter", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }).then(res => res.json())
        .then(data => {
            console.log(data)
            if (data["service"]["error"]) {
                this.setState({cred_error: error_text, cred_succ: ""})
            } else {
                this.setState({cred_succ: success_text, cred_error: ""})
            }
        })
    }

    set_keywords() {
        let data = {
            type: "keyword",
            keywords: this.state.keyword,
            start: this.state.start_date.toISOString().split("T")[0],
            end: this.state.end_date.toISOString().split("T")[0]
        }
        
        this.set_data(data, "Error in keywords settings", "Keywords set")
    }

    run() {
        fetch("http://localhost:8080/socket", {
            method: "GET",
        }).then(data => data.json())
        .then(data => {
            let socket = socketIOClient("http://localhost:8080")
            socket.emit("join", {room: data["socket"], service: "twitter"})
            socket.on("message", data => {
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
                    <h1>
                        Twitter Parameters
                    </h1>
                    <p style={{color: "red", marginTop: 5}}>{this.state.cred_error}</p>
                    <p style={{color: "green", marginTop: 5}}>{this.state.cred_succ}</p>
                </div>

                <h3 style={{marginTop: 115}}>
                    API Parameters
                </h3>
                <form onChange={(e) => console.log(e)}>
                    
                    <input type="text" value={this.state.cons_key} onChange={(e) => this.setState({cons_key: e.target.value})}/>
                    <input type="text" value={this.state.cons_sec} onChange={(e) => this.setState({cons_sec: e.target.value})}/>
                    <input type="text" value={this.state.acc_tok} onChange={(e) => this.setState({acc_tok: e.target.value})}/>
                    <input type="text" value={this.state.acc_sec} onChange={(e) => this.setState({acc_sec: e.target.value})}/>
                </form>

                <br></br>
                <button onClick={() => this.twitter_cred()}>Try credentials</button>
                
                <h3>
                    Keywords
                </h3>
                <form>
                    <input type="text" value="keywords" value={this.state.keyword} onChange={(e) => this.setState({keyword: e.target.value})}/>
                    <div className="grid">
                        <p>start date</p>    
                        <DatePicker value={this.state.start_date} onChange={e => this.setState({start_date: e})} />
                        <p>end date</p>    
                        <DatePicker value={this.state.end_date} onChange={e => this.setState({end_date: e})} />
                    </div>
                </form>

                <button onClick={() => this.set_keywords()}>Set Keywords</button>

                <h3>
                    Run crawling
                </h3>
                <button onClick={() => this.run()}>Run the crawling agent!</button>

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

                <h3>Results</h3>
                <h4>Images</h4>
                {this.state.images && this.state.images.map(image => <img src={image}/>)}

                <h4>Database</h4>
                <ReactJson style={{paddingBottom:20}} src={this.state.tweets}/>
                
            </div>
        )
    }
}