import graphene
from graphene_django.types import DjangoObjectType

from notes.models import Tag, Note, Revision, create_revision, create_note

class TagType(DjangoObjectType):
    class Meta:
        model = Tag

class RevisionType(DjangoObjectType):
    class Meta:
        model = Revision

class NoteType(DjangoObjectType):
    class Meta:
        model = Note
       
    latest_revision = graphene.Field(RevisionType)

class Query:
    all_tags = graphene.List(TagType)
    
    def resolve_all_tags(self, info, **kwargs):
        return Tag.objects.all()
        
    all_notes = graphene.List(NoteType)
    
    def resolve_all_notes(self, info, **kwargs):
        return Note.objects.all()

class CreateRevision(graphene.Mutation):
    class Arguments:
        note_id = graphene.ID()
        text = graphene.String()
        
    #use output typw
    revision = graphene.Field(RevisionType)
    
    def mutate(self, info, note_id, text):
        revision = create_revision(note_id, text)
        return CreateRevision(revision=revision)

class CreateNote(graphene.Mutation):
    class Arguments:
        pass

    note = graphene.Field(NoteType)

    def mutate(self, info):
        note = create_note()
        return CreateNote(note=note)

class Mutation:
    create_revision = CreateRevision.Field()
    create_note = CreateNote.Field()
