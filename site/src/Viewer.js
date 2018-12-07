import React, {Component} from "react";
import axios from "axios";
import "react-responsive-carousel/lib/styles/carousel.min.css";
import { Carousel } from 'react-responsive-carousel';
// import "./images/style_oil.png"

import imageOil from './images/style_oil.png';
// import imageHokusai from './images/style_hokusai.png';
import imageMarvel from './images/style_marvel.png';
import imageWaterColor from './images/style_watercolor.png';

class Viewer extends Component {

	constructor() {
		super();
		this.state = {
			value: 0,
			message: "Hello World!!",
			file: null
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
	};

	sendRequest = () => {
		let myData = {key1: 1000};
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
				<div className="btn btn-dark image-text">
					Select an Image
				</div>;
		} else {
			imageContent = <img src={this.state.file} alt={"Uploaded"} className="rounded-corners image-box"/>;
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
							<button type="button" className="btn btn-primary btn-lg btn-block">Begin Transfer</button>
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

export default Viewer;