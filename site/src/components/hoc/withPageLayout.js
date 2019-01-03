import React, {Component} from "react";

function withPageLayout(WrappedComponent) {

	return class extends Component {

		render() {
			return (
				<div className="container" role="main">
					<div className="row">

						<div className="col-12 highlight-test">
							<div className="jumbotron bg-dark top-margin text-center">
								<h1>STYLE TRANSFER</h1>
								<div className="sub-heading">VGG16 Style Transfer Web Demo</div>
							</div>
						</div>

						<WrappedComponent {...this.props}/>

						<div className="col-12">

							<div className="text-center footer-block">
								<p>Created by Jakrin Juangbhanich</p>

								<a href={"https://github.com/krinj/pytorch-style-transfer"}>
									<i className="fab fa-github bottom-icons"/>
								</a>

							</div>
						</div>

					</div>
				</div>
			);
		}
	};
}

export default withPageLayout;