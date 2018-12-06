import React, {Component} from 'react';

import 'bootstrap/dist/css/bootstrap.min.css';
import "./custom.css"
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
