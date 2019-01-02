import React, {Component} from "react";

function withImageSelectorLayout(WrappedComponent) {

	return class extends Component {

		render() {
			return (
				<div className="col-sm-12 col-md-6 highlight-test">
					<div className="highlight-block">
						<h5 className="no-margin top-margin">{this.props.title}</h5>
						{this.props.subTitle}
					</div>
					<div className="aspect-box">
						<label className="aspect-content">
							<WrappedComponent {...this.props} />
						</label>
					</div>
				</div>

			);
		}
	};
}

export default withImageSelectorLayout;