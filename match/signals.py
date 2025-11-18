from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Swipe
from .models import Match

@receiver(post_save, sender=Swipe)
def create_match(sender, instance, created, **kwargs):
    if not created:
        return 
    
    from_user = instance.from_user
    to_user = instance.to_user

    if instance.action in ['like', 'superlike']:

        # check if the other user liked back
        if Swipe.objects.filter(
            from_user=to_user,
            to_user=from_user,
            action__in=['like', 'superlike']
        ).exists():
            user1, user2 = sorted([from_user, to_user], key=lambda u: u.id)
            Match.objects.get_or_create(user1=user1, user2=user2)
    