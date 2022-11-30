
var Comment = React.createClass({
  rawMarkup: function() {
    var rawMarkup = marked(this.props.children.toString(), {sanitize: true});
    return { __html: rawMarkup };
  },

  render: function() {
    return (
     <li>
         <div className="col1">
            <div className="cont">
                <div className="cont-col1">
                    <div className="label label-sm label-success">
                        <i className="fa fa-cloud-download"></i>
                    </div>
                </div>
                <div className="cont-col2">
                    <div className="desc">
                        <a download={this.props.archive_name} href={this.props.archive_url}>
                            {this.props.company} - 
                            {this.props.created_by} - 
                            {this.props.datetime} - 
                            {this.props.archive_piece}
                        </a>
                    </div>
                </div>
            </div>
         </div>
     </li>


    );
  }
});




var Archives = React.createClass({

    loadArchiveListFromServer: function(){
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({data:data});
            }.bind(this),
            error: function(xhr, status, err){
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    getInitialState: function() {
        return {data: []};
    },

    componentDidMount: function() {
    this.loadArchiveListFromServer();
    setInterval(this.loadArchiveListFromServer, this.props.pollInterval);
    },


    render: function() {
        return (<ArchiveList data={this.state.data}/>);
    }

});

var ArchiveList = React.createClass({
    render: function(){
        var archiveNodes = this.props.data.map(function(archive) {
            return (
                <Comment datetime={archive.datetime} 
                         archive_name={archive.archive_name} 
                         archive_url={archive.archive_url} 
                         company={archive.company} 
                         key={archive.archive_name}
                         archive_piece={archive.archive_piece}
                         created_by={archive.created_by}>
                </Comment>
            );
        });
        return(
            <div>
                {archiveNodes}
            </div>
        );

    }
});




ReactDOM.render(
    <Archives url="/get_supervisor_archives_json" pollInterval={5000}/>,
    document.getElementById('test')

);
