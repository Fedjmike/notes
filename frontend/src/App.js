import React, {Component} from 'react';
import {QueryRenderer, createFragmentContainer, graphql} from 'react-relay'
import ContentEditable from 'react-contenteditable'
import TagsInput from 'react-tagsinput'

import environment from './Environment'

import CreateNoteMutation from './CreateNoteMutation'
import SetNoteTextMutation from './SetNoteTextMutation'
import SetNoteTagsMutation from './SetNoteTagsMutation'

import './App.css'

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
      SetNoteTextMutation(this.props.noteId, text, () => {console.log("success");}, () => {console.log("failure");});
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
  constructor(props) {
    super(props);
    
    this.state = {
      tags: this.props.note.latestRevision.tags.map(tag => tag.name)
    };
  }
  
  updateTags = (tags) => {
    this.setState({tags: tags});
    SetNoteTagsMutation(this.props.note.id, tags);
  }
  
  render() {
    const note = this.props.note;
    const text =   note.latestRevision
                 ? note.latestRevision.text
                 : "<em>The void</em>";
    
    return (
      <div className="note">
        <EditableNoteContent noteId={note.id} text={text} />
        <TagsInput value={this.state.tags} onChange={this.updateTags} />
      </div>
    );
  }
}

Note = createFragmentContainer(Note, {
  note: graphql`
    fragment App_note on NoteType {
      id
      latestRevision {
        text
        tags {
          name
        }
      }
    }
  `
});

class NoteList extends Component {
  constructor(props) {
    super(props);
    this.state = {notes: props.notes};
  }
  
  addNote = () => {
    CreateNoteMutation((response, error) => {
      var newNote = response.createNote.note;
      this.setState({notes: this.state.notes.concat([newNote])});
    }, () => {console.log("failure");});
  }

  render() {
    return (
      <div className="note-list">
        {this.state.notes.map((note) => {
          return <Note note={note} key={note.id} />
        })}
        <div>
          <button onClick={this.addNote}>+</button>
        </div>
      </div>
    );
  }
}

const AppQuery = graphql`
  query AppQuery {
    allNotes {
      ...App_note
    }
  }
`

class App extends Component {
  render() {
    return (
      <div className="App">
        <QueryRenderer
          environment={environment}
          query={AppQuery}
          render={({error, props}) => {
            if (error) {
              return <div>{error.message}</div>
            } else if (props) {
              return (
                <NoteList notes={props.allNotes} />
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
