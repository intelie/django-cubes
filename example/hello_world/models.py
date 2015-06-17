# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class IrbdBalance(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.CharField(max_length=256, blank=True)
    category_label = models.CharField(max_length=256, blank=True)
    subcategory = models.CharField(max_length=256, blank=True)
    subcategory_label = models.CharField(max_length=256, blank=True)
    line_item = models.CharField(max_length=256, blank=True)
    year = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'irbd_balance'
