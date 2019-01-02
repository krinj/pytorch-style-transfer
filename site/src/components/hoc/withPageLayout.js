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
								Do stuff.
							</div>
						</div>

						<WrappedComponent {...this.props}/>

						<div className="col-12 highlight-test">
							<div className="text-center footer-block">
								Created by Jakrin Juangbhanich
							</div>
						</div>

					</div>
				</div>
			);
		}
	};
}

export default withPageLayout;