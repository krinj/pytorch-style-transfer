import React, {Component} from "react";
import axios from "axios";

class Viewer extends Component {

	constructor() {
		super();
		this.state = {
			value: 0,
			message: "Hello World!!",
			file: null
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
		axios.post(`https://xliyrr4cp4.execute-api.ap-southeast-2.amazonaws.com/default/requestStyleTransfer`, myData)
			.then(this.getResponse)
	};

	onImageChange = (event) => {
		// POST to a test endpoint for demo purposes
		console.log("Item dropped");
		console.log(event);
		console.log(event.target.files.length);
		if (event.target.files.length > 0) {
			this.setState({
				file: URL.createObjectURL(event.target.files[0])
			});
		}
	};

	render() {

		let imageContent;
		if (this.state.file == null) {
			imageContent =
				<div className="btn btn-primary image-text">
					Select an Image
				</div>;
		} else {
			imageContent = <img src={this.state.file} alt={"Uploaded"} className="image-box"/>;
		}

		return (
			<div className="container" role="main">
				<div className="row">
					<div className="col-12 highlight-test">
						<div className="jumbotron bg-dark top-margin">
							<h1>Style Transfer App</h1>
							Do stuff.
						</div>
					</div>
					<div className="col-12 highlight-test">Explaination</div>

					<div className="col-sm-12 col-md-6 highlight-test flex">
						{/*<h4 className="text-center">Content Image</h4>*/}
						<div className="aspect-box">
						<label className="aspect-content">
							<input type="file" onChange={this.onImageChange} accept=".png, .jpg, .jpeg"/>
							<div className="image-container rounded-corners">
								<div className="image-container-inner rounded-corners">
									{imageContent}
								</div>
							</div>
						</label>
						</div>
					</div>

					<div className="col-sm-12 col-md-6 highlight-test">Style Image</div>
					<div className="col-12 highlight-test">Option to begin style transfer</div>
				</div>

				{/*<p>Template Runner</p>*/}
				{/*<p>{this.state.message}</p>*/}
				{/*<p>{`Clicks: ${this.state.value}`}</p>*/}
				{/*<button type="button" className="btn btn-primary" onClick={this.sendRequest}>Primary</button>*/}

				{/*<br/>*/}
				{/*<br/>*/}



			</div>
		);
	}
}

export default Viewer;