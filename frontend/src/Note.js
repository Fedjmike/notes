import React, {Component} from 'react';
import {createFragmentContainer, graphql} from 'react-relay'

import ContentEditable from 'react-contenteditable'
import TagsInput from 'react-tagsinput'

import SetNoteTextMutation from './SetNoteTextMutation'
import SetNoteTagsMutation from './SetNoteTagsMutation'

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
    fragment Note_note on NoteType {
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

export default Note
