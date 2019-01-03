import React, {Component} from "react";
import axios from "axios";
import imageOil from '../images/style_oil.png';
import imageMarvel from '../images/style_marvel.png';
import imageWaterColor from '../images/style_watercolor.png';
import { withRouter } from "react-router-dom";
import withPageLayout from "./hoc/withPageLayout";
import ImageUploader from "./ImageUploader";
import ImageSelector from "./ImageSelector";
import TransferButton from "./TransferButton";

class LandingPage extends Component {

	AppStateEnum = Object.freeze({
		"idle": 0,
		"waiting": 1,
		"error": 2
	});

	constructor() {
		super();

		// API Constants.

		this.styleImages = [imageOil, imageWaterColor, imageMarvel];
		this.styleTransferAPIEndpoint =
			"https://xliyrr4cp4.execute-api.ap-southeast-2.amazonaws.com/default/requestStyleTransfer";

		// Component State.

		this.state = {
			contentImageFile: null,
			contentImageUrl: null,
			styleImageIndex: 0,
			appState: this.AppStateEnum.idle
		}
	}

	// ============================================================================
	// Processing Functions: Upload the images and call the API.
	// ============================================================================

	convertImageToDataURL = (image, maxSize) => {

		let canvas = document.createElement('canvas');
		let context = canvas.getContext("2d");

		context.drawImage(image, 0, 0);
		let width = image.width;
		let height = image.height;

		// Rescale the image if needed.
		if (maxSize != null && maxSize > 0) {

			if (width > height) {
				if (height > maxSize) {
					width *= maxSize / height;
					height = maxSize;
				}
			} else {
				if (width > maxSize) {
					height *= maxSize / width;
					width = maxSize;
				}
			}
			canvas.width = width;
			canvas.height = height;
		}

		canvas.width = width;
		canvas.height = height;
		context = canvas.getContext("2d");
		context.drawImage(image, 0, 0, width, height);

		return canvas.toDataURL();
	};

	uploadStyleImage = (img) => {
		let dataUrl = this.convertImageToDataURL(img, 0);
		let fileReader = new FileReader();
		fileReader.addEventListener("load", (e) => {this.uploadContentImage(e, dataUrl)});
		fileReader.readAsDataURL(this.state.contentImageFile);
	};

	uploadContentImage = (e, styleImage) => {

		console.log("Downscaling the image...");
		console.log("Got Style Image " + styleImage);
		console.log(styleImage);

		let img = document.createElement("img");
		img.onload = () => {

			let dataUrl = this.convertImageToDataURL(img, 512);

			console.log("Got B64");
			console.log(dataUrl);

			let myData = {
				contentName: this.state.contentImageFile.name,
				contentData: dataUrl,
				styleName: imageOil,
				styleData: styleImage
			};

			axios.post(this.styleTransferAPIEndpoint, myData)
				.then(this.onServerResponse);
		};

		img.src = e.target.result;
	};

	onServerResponse = (res) => {
		// Received a response from our main server request.
		console.log(res);
		console.log(res.data);
		console.log(`Got Response ${res}`);

		// Extract the ID from the response, and route to the ID viewer.
		let id = res.data.id;
		this.props.history.push(`/display?id=${id}`);
	};

	// ============================================================================
	// Event Callbacks.
	// ============================================================================

	onTransferClick = () => {
		// User executes the style transfer.
		// Process and upload the images to our API.

		if (this.state.contentImageFile === null)
		{
			// No content image selected.
			this.setState({appState: this.AppStateEnum.error});
		}
		else if (this.state.appState !== this.AppStateEnum.waiting)
		{
			// App is not busy already.
			let img = document.createElement("img");
			img.onload = () => {
				this.uploadStyleImage(img)
			};
			img.src = this.styleImages[this.state.styleImageIndex];
			this.setState({appState: this.AppStateEnum.waiting});
		}
	};

	onContentImageChanged = (event) => {
		// A new image has been selected in the picker.
		console.log("OnContentImageChanged");
		if (event.target.files.length > 0) {
			this.setState({
				contentImageFile: event.target.files[0],
				contentImageUrl: URL.createObjectURL(event.target.files[0])
			});
		}
	};

	onStyleImageChanged = (i) => {
		// A different style image had been selected.
		console.log("Style Image Changed: " + i);
		this.setState({styleImageIndex: i});
	};

	// ============================================================================
	// Rendering.
	// ============================================================================

	render() {

		return (
			<div className="container" role="main">
				<div className="row">

					<ImageUploader
						title={"Content Image"}
						subTitle={"The image to transfer the style to."}
						onImageChanged={this.onContentImageChanged}
						imageUrl={this.state.contentImageUrl}
						isWaiting={this.state.appState === this.AppStateEnum.waiting}
					/>

					<ImageSelector
						title={"Style Image"}
						subTitle={"The image to transfer the style from."}
						images={this.styleImages}
						selectedImage={this.state.styleImageIndex}
						onImageChange={this.onStyleImageChanged}
						isWaiting={this.state.appState === this.AppStateEnum.waiting}
					/>

					<TransferButton
						onClick={this.onTransferClick}
						isWaiting={this.state.appState === this.AppStateEnum.waiting}
						isError={this.state.appState === this.AppStateEnum.error}
					/>

				</div>
			</div>
		);
	}
}

export default withRouter(withPageLayout(LandingPage));