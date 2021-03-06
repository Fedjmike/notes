import graphene
from graphene_django.types import DjangoObjectType

from notes.models import Tag, Note, Revision, create_note, revise_note, set_note_tags_by_name, search_notes

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
        
    search_notes = graphene.List(NoteType,
        tags=graphene.List(graphene.String, required=True)
    )
    
    def resolve_search_notes(self, info, **kwargs):
        return search_notes(kwargs.get("tags"))

class CreateNote(graphene.Mutation):
    class Arguments:
        pass

    note = graphene.Field(NoteType)

    def mutate(self, info):
        note = create_note()
        return CreateNote(note=note)

class SetNoteText(graphene.Mutation):
    class Arguments:
        note_id = graphene.ID(required=True)
        text = graphene.String(required=True)
        
    revision = graphene.Field(RevisionType)
    
    def mutate(self, info, note_id, text):
        revision = revise_note(note_id, {"text": text})
        return SetNoteText(revision=revision)

class SetNoteTagsByName(graphene.Mutation):
    class Arguments:
        note_id = graphene.ID(required=True)
        tags = graphene.List(graphene.String, required=True)
        
    revision = graphene.Field(RevisionType)
    
    def mutate(self, info, note_id, tags):
        revision = set_note_tags_by_name(note_id, tags)
        return SetNoteTagsByName(revision=revision)

class Mutation:
    create_note = CreateNote.Field()
    set_note_text = SetNoteText.Field()
    set_note_tags_by_name = SetNoteTagsByName.Field()
