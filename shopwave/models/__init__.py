#! -*- coding: utf-8 -*-

import json
from shopwave import fields
#from shopwave.manager import get_manager_class
from shopwave.models.base import Model

MODEL_LIST = [
    'Category',
    'Product',
    'Transaction',
    'BasketReport'
]

class Category(Model):
    id =            fields.IntField(primary_key=True)
    parentId =      fields.IntField()
    title =         fields.CharField(alias='n')
    activeDate =    fields.DateTimeField()
    deleteDate =    fields.DateTimeField()
    type =          fields.IntField()

    # Attributes that may be added from ReportBasket -> Category
    p =             fields.Reference(references='Product', blank=True)

class Product(Model):
    name =      fields.CharField(alias=['n'])
    id =        fields.IntField(primary_key=True)   # Product ID
    categories = fields.Reference(references=Category, attrname='title')

    activeDate = fields.DateTimeField()
    barcode =   fields.IntField(alias=['bC'])
    details =   fields.CharField()
    price =     fields.FloatField()
    productInstanceId = fields.IntField()
    productInstanceTimestamp = fields.DateTimeField()
    productTimestamp = fields.DateTimeField()
    size =      fields.FloatField()
    unit =      fields.CharField()
    vatPercentage = fields.FloatField()

    # Attributes that may be added from ReportBasket -> Transaction
    bPIId =     fields.IntField(blank=True)
    nt =        fields.CharField(blank=True)
    pIId =     fields.IntField(blank=True)
    pIP =       fields.CharField(blank=True, alt_name='Original Price')
    pMP =       fields.CharField(blank=True, alt_name='Modified Price')
    pMTP =      fields.CharField(blank=True)
    q =         fields.IntField(blank=True, alt_name='Quantity')
    vP =        fields.CharField(blank=True, alt_name='VAT Percentage')


class Transaction(Model):
    tId =   fields.IntField(primary_key=True)       # ID
    tA =    fields.IntField()                       # Amount
    tT =    fields.IntField()                       # Tax ??
    tTy =   fields.CharField()                      # Type {Cash/Card}
    bId =   fields.IntField()                       # Basket ID

class BasketReport(Model):
    bId =   fields.IntField(primary_key=True)
    bN =    fields.CharField(alt_name="Name")
    c =     fields.DateTimeField()
    cId =   fields.IntField()
    cd =    fields.IntField() 
    ch =    fields.IntField()
    sId =   fields.IntField(alt_name="Store ID")
    t =     fields.CharField(alt_name="Basket Total Service")
    p =     fields.Reference(references=Product)

    tr =    fields.Reference(references=Transaction)

