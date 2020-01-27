from django.db import models


class AbstractBaseModel(models.Model):
    """
    This abstract model contains fields that should be contained in each model. Soft delete is also implemented in this model.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self, commit=False):
        """
        Soft delete an instance.
        """

        self.is_deleted = True

        if commit:
            self.save()

    def undo_soft_delete(self, commit=False):
        """
        Undo soft delete of an instance.
        """

        self.is_deleted = False

        if commit:
            self.save()

    
    class Meta:
        abstract = True

class ActiveObjectsQuerySet(models.QuerySet):
    """
    This custom queryset filters results further and only returns objects
    that have not been soft deleted:
        ie, objects.all().filter(is_deleted=False)
    
    Because it returns a QuerySet, it can be filtered further as needed also.
        eg objects.all().filter(is_deleted=False).filter(is_active=True), etc
    
    https://docs.djangoproject.com/en/2.2/ref/models/querysets/
    """

    def _active(self):
        """
        Private method to filter results and only return objects that aren't soft deleted.
        """

        return self.filter(is_deleted=False)

    def all_objects(self):
        """
        Return all objects that aren't soft deleted.
        """

        return self._active()

