import React, {Component} from "react";
import {Alert} from "reactstrap";

class TransferButton extends Component {

	render() {

		let errorMessage = null;
		let buttonComponent = (
			<button type="button" className="btn btn-primary btn-lg btn-block" onClick={this.props.onClick}>
				Begin Transfer
			</button>
		);

		if (this.props.isWaiting) {
			buttonComponent = (
				<button type="button" className="btn btn-primary btn-lg btn-block" disabled>
					Uploading...
				</button>
			);
		}

		if (this.props.isError) {
			errorMessage = (
					<Alert color="warning">
						<b>Error</b>: Please upload a content image.
					</Alert>
			);
		}

		return (
			<>
				<div className="col-12 highlight-test">
					<div className="text-center v-margin">
						{errorMessage}
						{buttonComponent}
					</div>
				</div>
			</>
		);
	}
}

export default TransferButton;