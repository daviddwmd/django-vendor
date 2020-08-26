# import copy
# import random
# import string
# import uuid
# # import pycountry

# from django.conf import settings
# from django.contrib.sites.models import Site
# from django.core.exceptions import ValidationError
from django.db import models
# from django.db.models.signals import post_save
# from django.urls import reverse
# from django.utils import timezone
# from django.utils.text import slugify
from django.utils.translation import ugettext as _

# from address.models import AddressField
# from autoslug import AutoSlugField
# from iso4217 import Currency

from .base import CreateUpdateModelBase

###########
# WISHLIST
###########

class Wishlist(models.Model):
    profile = models.ForeignKey("vendor.CustomerProfile", verbose_name=_("Purchase Profile"), null=True, on_delete=models.CASCADE, related_name="wishlists")
    name = models.CharField(_("Name"), max_length=100, blank=False)

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")

    def __str__(self):
        return self.name


################
# WISHLIST ITEM
################

class WishlistItem(CreateUpdateModelBase):
    '''
    
    '''
    wishlist = models.ForeignKey(Wishlist, verbose_name=_("Wishlist"), on_delete=models.CASCADE, related_name="wishlist_items")
    offer = models.ForeignKey("vendor.Offer", verbose_name=_("Offer"), on_delete=models.CASCADE, related_name="wishlist_items")

    class Meta:
        verbose_name = _("Wishlist Item")
        verbose_name_plural = _("Wishlist Items")
        # TODO: Unique Name Per User

    def __str__(self):
        return "({}) {}: {}".format(self.wishlist.profile.user.username, self.wishlist.name, self.offer.name)
