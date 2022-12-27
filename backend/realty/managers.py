from django.db import models


class RentManager(models.Manager):

    def get_queryset(self):
        return super(RentManager, self).get_queryset().filter(type_of_negotiation='a')


class SaleManager(models.Manager):

    def get_queryset(self):
        return super(SaleManager, self).get_queryset().filter(type_of_negotiation='v')
