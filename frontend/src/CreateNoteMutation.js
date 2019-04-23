import {
  commitMutation,
  graphql,
} from 'react-relay'
import environment from './Environment'

export default (success, error) => {
  commitMutation(
    environment,
    {
      mutation: graphql`
        mutation CreateNoteMutation {
          createNote {
            note {
              ...Note_note
            }
          }
        }
      `,
      onCompleted: success,
      onError: error
    }
  )
}
