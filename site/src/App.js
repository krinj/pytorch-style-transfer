import React, {Component} from 'react';

import 'bootstrap/dist/css/bootstrap.min.css';
import "./custom.css"
import './App.css';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import Viewer from "./Viewer";
import Display from "./Display";


class App extends Component {
	render() {
		return (
			<Router>
				<div className="App">
					<header className="App-header">

						<Route exact path="/" component={Viewer} />
						<Route path="/display" component={Display} />

					</header>
				</div>
			</Router>
		);
	}
}

export default App;
