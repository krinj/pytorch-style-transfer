import React, {Component} from "react";
import {withRouter} from "react-router-dom";
import queryString from "query-string";
import axios from "axios/index";
import {Progress} from "reactstrap";

class Display extends Component {

	constructor() {
		super();
		this.state = {
			firstPing: false,
			progress: 0,
			exists: false,
			completed: false,
			resultImage: null,
			id: null
		}
	}

	getStats = () => {

		let requestData = {
			id: this.state.id
		};

		console.log("Posting to API");
		console.log(requestData);

		axios.post(`https://9yokb5ep80.execute-api.ap-southeast-2.amazonaws.com/default/getStyleTransferStatus`, requestData)
			.then(this.getStatusResponse);
	};

	getStatusResponse = (res) => {
		console.log(res);
		console.log(res.data);
		console.log(res.data.body);

		let data = JSON.parse(res.data.body);
		console.log(data);

		console.log(`Got Response ${res}`);

		const newState = {...this.state};
		newState.exists = data.exists;
		newState.progress = data.progress;
		newState.completed = data.completed;
		newState.resultImage = data.result_image;
		newState.firstPing = true;
		this.setState(newState);

		// If the image exists but is still processing, then keep upading the progress.
		if (data.progress < 100 && data.exists) {
			setTimeout(this.getStats, 5000);
		}
	};

	getBodyContent = () => {
		console.log("Progress: " + this.state.progress);
		console.log("Exists: " + this.state.exists);
		console.log("Result URL: " + this.state.resultImage);

		let contentHeading = null;
		let progressSection = null;
		let imageSection = null;

		if (this.state.exists) {
			if (this.state.progress < 100) {
				if (this.state.progress === 0) {
					contentHeading = <p className="text-center lead">Provisioning Containers</p>;
					progressSection = <div className="auto-margin loader"/>;
				} else {
					contentHeading = <p className="text-center lead">Content Rendering</p>;
					progressSection = <Progress animated value={this.state.progress}/>
				}
			} else {
				contentHeading = <p className="text-center lead">Content Rendered</p>;
			}
		} else {
			contentHeading = <p className="text-center lead">Content Not Found</p>;
		}

		if (this.state.exists && this.state.progress === 100 && this.state.resultImage !== null)
		{
			imageSection = (
				<div className="aspect-box">
					<label className="aspect-content">
						<input type="file" onChange={this.onImageChange} accept=".png, .jpg, .jpeg"/>
						<div className="image-container rounded-corners">
							<div className="image-container-inner rounded-corners">
								<img src={this.state.resultImage} alt={"Uploaded"} className="rounded-corners image-box"/>
							</div>
						</div>
					</label>
				</div>
			);
		}

		return (
			<div>
				{contentHeading}
				{progressSection}
				{imageSection}
			</div>
		);
	};

	componentWillMount = () => {
		console.log(this.props.location.search);
		let params = queryString.parse(this.props.location.search);
		console.log(params);
		this.setState({id: params.id});
	};

	render() {

		let id = this.state.id;

		if (this.state.firstPing === false) {
			this.getStats();
		}

		// Do an API call to check either the progress or display the results.
		// this.getStats(id);
		let bodyContent = this.getBodyContent();
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
							Checking the content of ID: {id}
						</p>
					</div>

					<div className="col-12 highlight-test">
						{bodyContent}
					</div>

					<div className="col-12 highlight-test">
						<div className="text-center footer-block">
							Created by Jakrin Juangbhanich
						</div>
					</div>
				</div>
			</div>
		);
	}
}

export default withRouter(Display);