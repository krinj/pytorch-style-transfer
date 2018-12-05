import React, {Component} from 'react';
import logo from './logo.svg';
import './App.css';
import Viewer from "./Viewer";

class App extends Component {
	render() {
		return (
			<div className="App">
				<header className="App-header">
					<Viewer/>
				</header>
			</div>
		);
	}
}

export default App;
