import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import axios from 'axios'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      response: '',
      messages: []
    };
  }

  componentDidMount() {
    this.callApi()
      .then(res => this.setState({ response: res.first_name }))
      .catch(err => console.log(err));

      var ws = new WebSocket("ws://localhost:8888/echo/");
        ws.onopen = function() {
        ws.send("Hello, world");
      };
      ws.onmessage = evt => { 
        // add the new message to state
          this.setState({
          messages : this.state.messages.concat([ evt.data ])
        })
      };
  }

  callApi = async () => {
    const response = await fetch('/hello/');
    const body = await response.json();

    if (response.status !== 200) throw Error(body.message);

    return body;
  };

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome to React</h1>
        </header>
        <p className="App-intro">{this.state.response}</p>
        <p className="App-intro">{this.props.in1}</p>
        <ul>{ this.state.messages.map( (msg, idx) => <li key={'msg-' + idx }>{ msg }</li> )}</ul>
      </div>
    );
  }
}

export default App;
