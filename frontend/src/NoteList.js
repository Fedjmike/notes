import React, {Component} from 'react';

import Note from './Note'
import CreateNoteMutation from './CreateNoteMutation'

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

export default NoteList
