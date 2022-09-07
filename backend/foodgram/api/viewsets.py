from rest_framework import mixins, viewsets


class ReadViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """Миксин чтения списка и опреденных объектов"""
    pass


class ReadListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Миксин чтения списка объектов"""
    pass


class CreateReadViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Миксин создания объектов и чтения списка и опреденных объектов"""
    pass


class CreateDeleteViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin,
                          mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Миксин создания и удаления опреденных объектов"""
    pass
