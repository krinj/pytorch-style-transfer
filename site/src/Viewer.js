import React, {Component} from "react";
import axios from "axios";
import "react-responsive-carousel/lib/styles/carousel.min.css";
import { Carousel } from 'react-responsive-carousel';
// import "./images/style_oil.png"

import imageOil from './images/style_oil.png';
// import imageHokusai from './images/style_hokusai.png';
import imageMarvel from './images/style_marvel.png';
import imageWaterColor from './images/style_watercolor.png';
import { withRouter } from "react-router-dom";

class Viewer extends Component {

	constructor() {
		super();
		this.state = {
			value: 0,
			message: "Hello World!!",
			file: null,
			fileUrl: null
		}
	}

	// doSomething = () => {
	// 	console.log(`DoSomething ${this.state.value}`);
	// 	console.log(this);
	//
	// 	const newState = {...this.state};
	// 	newState.value += 1;
	// 	this.setState(newState);
	// };

	getResponse = (res) => {
		console.log(res);
		console.log(res.data);
		console.log(`Got Response ${res}`);
		const newState = {...this.state};
		newState.value = res.data.k2;
		newState.message = res.data.k1;
		this.setState(newState);

		let id = res.data.id;
		this.props.history.push(`/display?id=${id}`);
	};

	getBase64Result = (e) => {
		console.log("Got B64");
		console.log(e.target.result);

		let myData = {
			key1: 1000,
			fileName: this.state.file.name,
			fileData: e.target.result
		};

		axios.post(`https://xliyrr4cp4.execute-api.ap-southeast-2.amazonaws.com/default/requestStyleTransfer`, myData)
			.then(this.getResponse);
	};

	downscaleImage = (e) => {
		console.log("Downscaling the image...");

		let img = document.createElement("img");
		img.onload = () => {
			let canvas = document.createElement('canvas');
			let context = canvas.getContext("2d");
			context.drawImage(img, 0, 0);

			let MAX_WIDTH = 400;
			let MAX_HEIGHT = 400;
			let width = img.width;
			let height = img.height;

			if (width > height) {
				if (width > MAX_WIDTH) {
					height *= MAX_WIDTH / width;
					width = MAX_WIDTH;
				}
			} else {
				if (height > MAX_HEIGHT) {
					width *= MAX_HEIGHT / height;
					height = MAX_HEIGHT;
				}
			}

			canvas.width = width;
			canvas.height = height;

			context = canvas.getContext("2d");
			context.drawImage(img, 0, 0, width, height);

			let dataUrl = canvas.toDataURL();

			console.log("Got B64");
			console.log(dataUrl);

			let myData = {
				fileName: this.state.file.name,
				fileData: dataUrl
			};

			axios.post(`https://xliyrr4cp4.execute-api.ap-southeast-2.amazonaws.com/default/requestStyleTransfer`, myData)
				.then(this.getResponse);

			// console.log(dataUrl);
			// let fileReader = new FileReader();
			// fileReader.addEventListener("load", this.getBase64Result);
			// fileReader.readAsDataURL(dataUrl);
		};
		img.src = e.target.result;
	};

	sendRequest = () => {
		// this.props.history.push("/display?id=1234");
		let fileReader = new FileReader();
		fileReader.addEventListener("load", this.downscaleImage);
		fileReader.readAsDataURL(this.state.file);
	};

	onImageChange = (event) => {
		// POST to a test endpoint for demo purposes
		console.log("Item dropped");
		console.log(event);
		console.log(event.target.files.length);
		if (event.target.files.length > 0) {
			this.setState({
				file: event.target.files[0],
				fileUrl: URL.createObjectURL(event.target.files[0])
			});
		}
	};

	render() {

		let imageContent;
		if (this.state.file == null) {
			imageContent =
				<div className="btn btn-dark image-text">
					Select an Image
				</div>;
		} else {
			imageContent = <img src={this.state.fileUrl} alt={"Uploaded"} className="rounded-corners image-box"/>;
		}

		return (
			<div className="container" role="main">
				<div className="row">
					<div className="col-12 highlight-test">
						<div className="jumbotron bg-dark top-margin text-center">
							<h1>STYLE TRANSFER</h1>
							Do stuff.
						</div>
					</div>
					<div className="col-12 highlight-test">
						<p className="text-center lead">
							This is a description of the style transfer app from Udacity.
						</p>
					</div>

					<div className="col-sm-12 col-md-6 highlight-test">
						<div className="highlight-block">
							<h5 className="no-margin top-margin">Content Image</h5>
							Say something about the style box.
						</div>
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

					<div className="col-sm-12 col-md-6 highlight-test">
						<div className="highlight-block">
							<h5 className="no-margin top-margin">Style Image</h5>
							Say something about the style box.
						</div>
						<div className="aspect-box">
							<label className="aspect-content">
								{/*<input type="file" onChange={this.onImageChange} accept=".png, .jpg, .jpeg"/>*/}
								<div className="image-container rounded-corners">
									{/*<div className="image-container-inner rounded-corners">*/}

										<Carousel showThumbs={false} showStatus={false} showIndicators={false} swipeScrollTolerance={50}
															infiniteLoop={true}
															className="image-container-inner rounded-corners">
											<div>
												<img src={imageWaterColor} alt={"Style1"} className="image-box rounded-corners"/>
												{/*<p className="legend">Legend 1</p>*/}
											</div>
											<div>
												<img src={imageMarvel} alt={"Style2"} className="image-box rounded-corners"/>
												{/*<p className="legend">Legend 2</p>*/}
											</div>
											<div>
												<img src={imageOil} alt={"Style3"} className="image-box rounded-corners"/>
												{/*<p className="legend">Legend 3</p>*/}
											</div>
										</Carousel>

									{/*</div>*/}
								</div>
							</label>
						</div>
					</div>

					<div className="col-12 highlight-test">
						<div className="text-center v-margin">
							<button type="button" className="btn btn-primary btn-lg btn-block" onClick={this.sendRequest}>
								Begin Transfer
							</button>
						</div>
					</div>

					<div className="col-12 highlight-test">
						<div className="text-center footer-block">
							Created by Jakrin Juangbhanich
						</div>
					</div>
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

export default withRouter(Viewer);