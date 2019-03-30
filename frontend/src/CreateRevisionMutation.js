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
        mutation CreateRevisionMutation($noteId: ID, $text: String) {
          createRevision(noteId: $noteId, text: $text) {
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
