import React, {Component} from "react";
import withImageSelectorLayout from "./hoc/withImageSelectorLayout";
import { Carousel } from 'react-responsive-carousel';
import "react-responsive-carousel/lib/styles/carousel.min.css";

class ImageSelector extends Component {

	/* Select an image from a list of available images. */

	render() {

		let inputComponent = null;
		let images = this.props.images;

		if (!this.props.isWaiting)
		{

			let imageRenderList = [];

			for (let i = 0; i < images.length; i++)
			{
				imageRenderList.push(
					<div key={i}>
						<img src={images[i]} alt={"Style" + i} className="image-box rounded-corners"/>
					</div>
				)
			}

			inputComponent = (
				<Carousel showThumbs={false} showStatus={false} showIndicators={false} swipeScrollTolerance={50}
									infiniteLoop={true}
									onChange={this.props.onImageChange}
									selectedItem={this.props.selectedImage}
									className="image-container-inner rounded-corners">
					{imageRenderList}
				</Carousel>
			);

		} else {

			inputComponent = (
				<div className="image-container-inner rounded-corners">
					<img src={images[this.props.selectedImage]} alt={"SelectedStyle"} className="rounded-corners image-box"/>
				</div>
			);
		}

		return (
			<>
				<div className="image-container rounded-corners">
					{inputComponent}
				</div>
			</>
		);
	}
}

export default withImageSelectorLayout(ImageSelector);