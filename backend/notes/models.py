from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

class Note(models.Model):
    tags = models.ManyToManyField(Tag, related_name="notes")
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    @property
    def latest_revision(self):
        try:
            return self.revisions.latest("created")
        
        except models.Model.DoesNotExist:
            return None
    
class Revision(models.Model):
    note = models.ForeignKey(Note, on_delete=models.PROTECT, related_name="revisions")
    
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
def create_revision(note_id, text):
    revision = Revision(text=text, note=Note.objects.get(id=note_id))
    revision.save()
    return revision

def create_note(text="", tag_ids=[]):
    note = Note()
    note.save()
    note.tags.set(Tag.objects.filter(id__in=tag_ids))
    Revision.objects.create(text=text, note=note)
    return note
