from django.test import TestCase

from notes.models import Tag, Note, Revision, create_note
from backend.schema import schema

def create_some_data():
    ts = [Tag.objects.create(name="t%d" % n) for n in range(3)]
    
    n0 = create_note(text="n0r0", tag_ids=[ts[n].id for n in [0, 1]])
    
    return n0
    
class ModelTest(TestCase):
    def test_model(self):
        n0 = create_some_data()
        
        self.assertEqual(n0.latest_revision.text, "n0r0")
        self.assertEqual([t.name for t in n0.tags.all()], ["t0", "t1"])
        
class SchemaTest(TestCase):
    def run_query(self, query, **kwargs):
        result = schema.execute(query, variables=kwargs)
        
        if result.errors: print(result.errors)
        self.assertEqual(result.errors, None)
        
        import json
        print(json.dumps(result.to_dict()))
    
    def test_notes_schema(self):
        create_some_data()
        query = """
        query {
            allNotes {
                created,
                revisions {
                    text
                },
                tags {
                    name
                }
            }
        }
        """
        self.run_query(query)
        
    def test_tags_schema(self):
        create_some_data()
        query = """
        query {
            allTags {
                name,
                notes {
                    created
                    revisions {
                        text
                    }
                }
            }
        }
        """
        self.run_query(query)
        
    def test_revision_mutation(self):
        n0 = create_some_data()
        
        query = """
        mutation ($noteId: ID) {
            createRevision(noteId: $noteId, text: "n0r1") {
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
        self.run_query(query, noteId=n0.id)

    def test_note_mutation(self):
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
        self.run_query(query)
