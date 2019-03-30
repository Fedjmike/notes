import React, {Component} from 'react';
import {QueryRenderer, graphql} from 'react-relay'
import ContentEditable from 'react-contenteditable'

import environment from './Environment'

import CreateRevisionMutation from './CreateRevisionMutation'

const NotesQuery = graphql`
  query AppQuery {
    allNotes {
      id
      created
      modified
      latestRevision {
        text
        created
      }
      revisions {
        text
        created
      }
    }
  }
`

class EditableNoteContent extends Component {
  constructor(props) {
    super(props);
    this.contentEditable = React.createRef();
    this.state = {html: this.props.text};
  }
  
  handleChange = e => {
    var text = this.contentEditable.current.innerHTML;
    
    if (text !== this.state.html) {
        this.setState({html: text});
        CreateRevisionMutation(this.props.noteId, text, () => {console.log("success");}, () => {console.log("failure");});
    }
  }
  
  render() {
    return (
      <ContentEditable
        innerRef={this.contentEditable}
        html={this.state.html}
        onBlur={this.handleChange}
      />
    )
  }
}

class Note extends Component {
  render() {
    return (
      <div className="note">
        <EditableNoteContent noteId={this.props.note.id} text={this.props.note.latestRevision.text} />
      </div>
    );
  }
}  

class App extends Component {
  render() {
    return (
      <div className="App">
        <QueryRenderer
          environment={environment}
          query={NotesQuery}
          render={({error, props}) => {
            if (error) {
              return <div>{error.message}</div>
            } else if (props) {
              return (
                <div>
                  {props.allNotes.map((note) => {
                    return <Note note={note} key={note.id} />
                  })}
                </div>
              );
            } else {
              return <div>Loading</div>
            }
          }}
        />
      </div>
    );
  }
}

export default App;
