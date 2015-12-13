def class_name_pk(self):
    """

    Django Admin object names based on class and pk, e.g.:

    client-1
    client-2
    client-3
    """
    return '-'.join([self.__class__.__name__.lower(), str(self.pk)])
