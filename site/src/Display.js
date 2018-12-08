import React, {Component} from "react";
import { withRouter } from "react-router-dom";
import queryString from "query-string";

class Display extends Component {
	render() {
		console.log(this.props.location.search);
		let params = queryString.parse(this.props.location.search);
		console.log(params);
		let id = params.id;
		return (
			<div>Display Results for ID: {id}</div>
		);
	}
}

export default withRouter(Display);