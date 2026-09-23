import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Note

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Note)
def embed_note_on_save(sender, instance, **kwargs):
    from ai_search.services import embed_note

    try:
        embed_note(
            instance.pk, instance.title, instance.body, owner_id=instance.owner_id
        )
    except Exception:
        logger.exception("Failed to embed note %s into Pinecone", instance.pk)


@receiver(post_delete, sender=Note)
def remove_note_embedding_on_delete(sender, instance, **kwargs):
    from ai_search.pinecone_client import delete_vector

    try:
        delete_vector(instance.pk)
    except Exception:
        logger.exception("Failed to delete Pinecone vector for note %s", instance.pk)
