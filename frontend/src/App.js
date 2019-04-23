import React, {Component} from 'react';
import {QueryRenderer, graphql} from 'react-relay'

import environment from './Environment'

import NoteList from './NoteList'

import './App.css'

const AppQuery = graphql`
  query AppQuery {
    allNotes {
      ...Note_note
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
