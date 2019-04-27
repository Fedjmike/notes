from django.db import models
from django.db.models.expressions import F
from django.db.models.aggregates import Max

from functools import reduce
from copy import copy

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)

class Note(models.Model):
    @property
    def latest_revision(self):
        try:
            return self.revisions.latest("created")
        
        except models.Model.DoesNotExist:
            return None
            
    @property
    def first_revision(self):
        try:
            return self.revisions.earliest("created")
        
        except models.Model.DoesNotExist:
            return None
    
class Revision(models.Model):
    note = models.ForeignKey(Note, on_delete=models.PROTECT, related_name="revisions")
    
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)

def create_note(text="", tag_ids=[]):
    note = Note.objects.create()
    revision = Revision.objects.create(text=text, note=note)
    revision.tags.set(Tag.objects.filter(id__in=tag_ids))
    return note

def create_revision_copy(note_id):
    """Creates a new revision by duplicating the latest revision."""
    
    latest_revision = Note.objects.get(id=note_id).latest_revision
    
    #Create a copy detached from the row it came from, and save it as a new row
    revision = copy(latest_revision)
    revision.pk = None
    #When saving, the "created" datetime is automatically set to now
    revision.save()
    
    #ManyToManyFields are represented by separate tables and must be copied manually
    revision.tags.set(latest_revision.tags.all())
    
    return revision
    
def revise_note(note_id, new_values):
    """Creates a new revision of an existing note by updating the revision
       columns specified by a dict `new_values`."""
    
    revision = create_revision_copy(note_id)
    
    for column, value in new_values.items():
        setattr(revision, column, value)
        
    revision.save()
    return revision
    
def set_note_tags_by_name(note_id, tag_names):
    #Get the tags already present in the db
    tag_names = set(tag_names)
    tags_which_exist = Tag.objects.filter(name__in=tag_names)
    
    #Create any new tags
    tag_names_which_dont_exist = tag_names - set(tags_which_exist.values_list("name", flat=True))
    new_tags = [Tag.objects.create(name=name) for name in tag_names_which_dont_exist]
    
    tags = list(tags_which_exist) + new_tags
    
    revision = create_revision_copy(note_id)
    revision.tags.set(tags)
    return revision

def search_notes(tag_names):
    latest_revisions = Revision.objects \
        .annotate(note_updated=Max("note__revisions__created")) \
        .filter(note_updated=F("created"))
    
    #Add a filter for each tag
    #(If one filter were used for all tags, it would look for a single tag row
    # which matched every name, in the result of only one join).
    matching_latest_revisions = reduce(
        lambda revisions, tag_name: revisions.filter(tags__name=tag_name),
        tag_names, latest_revisions
    )
    
    return (r.note for r in matching_latest_revisions)
