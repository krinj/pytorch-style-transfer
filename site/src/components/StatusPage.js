import React, {Component} from "react";
import {withRouter} from "react-router-dom";
import queryString from "query-string";
import axios from "axios/index";
import {Progress} from "reactstrap";
import withPageLayout from "./hoc/withPageLayout";

class StatusPage extends Component {

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

	getHeaderText = () => {
		if (this.state.firstPing) {
			if (this.state.exists) {
				if (this.state.progress < 100) {
					if (this.state.progress === 0) {
						// Still booting up the containers.
						return "Provisioning Containers";
					} else {
						// Container is working.
						return "Rendering";
					}
				} else {
					// Content has finished.
					return "Transfer Complete";
				}
			} else {
				// Job doesn't exist.
				return "Content Not Found";
			}
		} else {
			// Load the job details.
			return "Checking Status";
		}
	};

	getBodyContent = () => {

		console.log("Progress: " + this.state.progress);
		console.log("Exists: " + this.state.exists);
		console.log("Result URL: " + this.state.resultImage);

		let progressSection = null;
		let imageSection = null;

		if (this.state.firstPing) {
			if (this.state.exists) {
				if (this.state.progress < 100) {
					if (this.state.progress === 0) {
						// Still booting up the containers.
						progressSection = <div className="auto-margin loader"/>;
					} else {
						// Container is working.
						progressSection = <Progress animated value={this.state.progress}/>
					}
				}
			}
		} else {
			progressSection = <div className="auto-margin loader"/>;
		}

		if (this.state.exists && this.state.progress === 100 && this.state.resultImage !== null)
		{
			imageSection = (
				<>
					<div className="aspect-box">
						<label className="aspect-content">
							<div className="image-container rounded-corners">
								<div className="image-container-inner rounded-corners">
									<img src={this.state.resultImage} alt={"Uploaded"} className="rounded-corners image-box"/>
								</div>
							</div>
						</label>
					</div>
					<form method="get" action={this.state.resultImage}>
						<button type="submit" className="btn btn-primary btn-lg btn-block">
							Download
						</button>
					</form>
				</>
			);
		}

		return (
			<div>
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
		let headerText = this.getHeaderText();

		return (
					<>

						<div className="col-12 highlight-test text-center">
							<h6><b>{headerText}</b></h6>
							{id}
						</div>

						<div className="col-12 highlight-test top-margin">
							{bodyContent}
						</div>
					</>
		);
	}
}

export default withRouter(withPageLayout(StatusPage));