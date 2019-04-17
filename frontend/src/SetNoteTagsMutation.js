import {
  commitMutation,
  graphql,
} from 'react-relay'
import environment from './Environment'

export default (noteId, tags, success, error) => {
  commitMutation(
    environment,
    {
      mutation: graphql`
        mutation SetNoteTagsMutation($noteId: ID!, $tags: [String]!) {
          setNoteTagsByName(noteId: $noteId, tags: $tags) {
            revision {
              id
            }
          }
        }
      `,
      variables: {noteId: noteId, tags: tags},
      onCompleted: success,
      onError: error
    }
  )
}

