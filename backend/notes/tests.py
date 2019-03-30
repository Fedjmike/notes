from django.test import TestCase

from notes.models import Tag, Note, Revision
from backend.schema import schema

def create_some_data():
    ts = [Tag(name="t%d" % n) for n in range(3)]
    for t in ts: t.save()
    
    n = Note()
    n.save()
    n.tags.set([ts[0], ts[1]])
    n.save()
    
    r = Revision(text="n0r0", note=n)
    r.save()
    
    return r
    
class ModelTest(TestCase):
    def test_model(self):
        r = create_some_data()
        
        self.assertEqual(r.text, "n0r0")
        self.assertEqual([t.name for t in r.note.tags.all()], ["t0", "t1"])
        #print([t.notes.all() for t in Tag.objects.all()])
        
    #def test_latest_revision
        
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
        n0r0 = create_some_data()
        
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
        self.run_query(query, noteId=n0r0.note.id)

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
