import React, {Component} from "react";
import withImageSelectorLayout from "./hoc/withImageSelectorLayout";

class ImageUploader extends Component {
	render() {

		let imageContent;
		if (this.props.imageUrl == null) {
			imageContent =
				<div className="btn btn-dark image-text">
					Select an Image
				</div>;
		} else {
			imageContent = <img src={this.props.imageUrl} alt={"Uploaded"} className="rounded-corners image-box"/>;
		}

		let inputComponent = null;
		if (!this.props.isWaiting)
		{
			inputComponent = <input type="file" onChange={this.props.onImageChanged} accept=".png, .jpg, .jpeg"/>
		}

		return (
			<>
				{inputComponent}
				<div className="image-container rounded-corners">
					<div className="image-container-inner rounded-corners">
						{imageContent}
						</div>
				</div>
			</>
		);
	}
}

export default withImageSelectorLayout(ImageUploader);