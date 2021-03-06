from django.test import TestCase

from notes.models import Tag, Note, Revision, create_note, create_revision_copy, revise_note, set_note_tags_by_name
from backend.schema import schema

def create_some_data():
    ts = [Tag.objects.create(name="t%d" % n) for n in range(3)]
    
    n0 = create_note(text="n0r0", tag_ids=[ts[n].id for n in [0, 1]])
    
    n0r1 = revise_note(n0.id, {"text": "n0r1"})
    n0r2 = set_note_tags_by_name(n0.id, ["t1", "t2"])
    
    return n0
    
class ModelTest(TestCase):
    def test_model(self):
        n0 = create_some_data()
        
        self.assertEqual(n0.first_revision.text, "n0r0")
        self.assertEqual(n0.latest_revision.text, "n0r1")
        self.assertEqual([t.name for t in n0.latest_revision.tags.all()], ["t1", "t2"])
        
class SchemaTest(TestCase):
    def run_query(self, query, **kwargs):
        result = schema.execute(query, variables=kwargs)
        
        if result.errors:
            if len(result.errors) == 1:
                raise result.errors[0]
            
            else:
                raise result.errors
        
        return result.data
    
    def test_notes_schema(self):
        create_some_data()
        query = """
        query {
            allNotes {
                latestRevision {
                    text
                    tags {
                        name
                    }
                }
            }
        }
        """
        data = self.run_query(query)
        self.assertEqual(data["allNotes"][0]["latestRevision"]["text"], "n0r1")
        
    def test_create_note(self):
        query = """
        mutation {
            createNote {
                note {
                    revisions {
                        text
                    }
                }
            }
        }
        """
        data = self.run_query(query)["createNote"]
        self.assertEqual(len(data["note"]["revisions"]), 1)
        self.assertEqual(data["note"]["revisions"][0]["text"], "")

    def test_set_note_text(self):
        n0 = create_some_data()
        
        query = """
        mutation ($noteId: ID!) {
            setNoteText(noteId: $noteId, text: "n0r3") {
                revision {
                    text
                    note {
                        latestRevision {
                            text
                        }
                    }
                }
            }
        }
        """
        data = self.run_query(query, noteId=n0.id)["setNoteText"]
        self.assertEqual(data["revision"]["text"], "n0r3")
        self.assertEqual(data["revision"]["note"]["latestRevision"]["text"], "n0r3")
        
    def test_set_note_tags(self):
        n0 = create_some_data()
        
        query = """
        mutation ($noteId: ID!) {
            setNoteTagsByName(noteId: $noteId, tags: ["t2", "t3"]) {
                revision {
                    tags {
                        id, name
                    }
                }
            }
        }
        """
        data = self.run_query(query, noteId=n0.id)["setNoteTagsByName"]
        
        self.assertEqual([t["name"] for t in data["revision"]["tags"]], ["t2", "t3"])
        #Ensure that only one new tag (t3) has been created
        self.assertEqual(Tag.objects.count(), 4)

    def test_search(self):
        def search(tags, expected_note_texts):
            query = """
            query ($tags: [String!]!) {
                searchNotes(tags: $tags) {
                    latestRevision {
                        text
                        tags {name}
                    }
                }
            }
            """
            data = self.run_query(query, tags=tags)["searchNotes"]
            self.assertEqual([note["latestRevision"]["text"] for note in data], expected_note_texts)
            
            #Check that all the search results have the expected tags
            for note in data:
                note_tags = (t["name"] for t in note["latestRevision"]["tags"])
                self.assertLessEqual(set(tags), set(note_tags))
                
        def tag_ids(*names):
            return [Tag.objects.get(name=name).id for name in names]
            
        n0 = create_some_data()
        
        create_note("n1", tag_ids=tag_ids("t0", "t1", "t2"))
        create_note("n2", tag_ids=tag_ids("t0", "t1"))
        create_note("n3", tag_ids=tag_ids("t2"))
        
        search(["t0"], expected_note_texts=["n1", "n2"])
        search(["t1"], expected_note_texts=[n0.latest_revision.text, "n1", "n2"])
        search(["t2"], expected_note_texts=[n0.latest_revision.text, "n1", "n3"])
        
        search(["t0", "t2"], expected_note_texts=["n1"])
        search(["t0", "t1"], expected_note_texts=["n1", "n2"])
