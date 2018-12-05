import React, {Component} from "react";
import axios from "axios";

class Viewer extends Component {

	constructor() {
		super();
		this.state = {
			value: 0,
			message: "Hello World!!"
		}
	}

	doSomething = () => {
		console.log(`DoSomething ${this.state.value}`);
		console.log(this);

		const newState = {...this.state};
		newState.value += 1;
		this.setState(newState);
	};

	getResponse = (res) => {
		console.log(res);
		console.log(res.data);
		console.log(`Got Response ${res}`);
		const newState = {...this.state};
		newState.value = res.data.k2;
		newState.message = res.data.k1;
		this.setState(newState);
	};

	sendRequest = () => {
		let myData= {key1: 1000};
		// let config = {
		// 	headers: {
		// 		'Content-Type': 'application/json',
		// 	}
		// };
		axios.post(`https://xliyrr4cp4.execute-api.ap-southeast-2.amazonaws.com/default/requestStyleTransfer`, myData)
			.then(this.getResponse)
	};

	render() {
		return (
			<div className="container theme-showcase" role="main">

				<div>Hello</div>
				<div className="jumbotron bg-dark">
					<h1>Theme example</h1>
				</div>

				<p>Template Runner</p>
				<p>{this.state.message}</p>
				<p>{`Clicks: ${this.state.value}`}</p>
				<button type="button" className="btn btn-primary" onClick={this.sendRequest}>Primary</button>

			</div>
			// <div>
			// 	<div className="container theme-showcase" role="main">
			//
			// 		<!-- Main jumbotron for a primary marketing message or call to action -->
			// 		<div className="jumbotron">
			// 			<h1>Theme example</h1>
			// 			<p>This is a template showcasing the optional theme stylesheet included in Bootstrap. Use it as a starting
			// 				point to create something more unique by building on or modifying it.</p>
			// 		</div>
			//
			// 		<p>Template Runner</p>
			// 		<p>{this.state.message}</p>
			// 		<p>{`Clicks: ${this.state.value}`}</p>
			// 		<button type="button" className="btn btn-primary" onClick={this.doSomething}>Primary</button>
			//
			// 	</div>
			// </div>
		);
	}
}

export default Viewer;