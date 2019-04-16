import {
  commitMutation,
  graphql,
} from 'react-relay'
import environment from './Environment'

export default (noteId, text, success, error) => {
  commitMutation(
    environment,
    {
      mutation: graphql`
        mutation SetNoteTextMutation($noteId: ID!, $text: String!) {
          setNoteText(noteId: $noteId, text: $text) {
            revision {
              id
            }
          }
        }
      `,
      variables: {noteId: noteId, text: text},
      onCompleted: success,
      onError: error
    }
  )
}
