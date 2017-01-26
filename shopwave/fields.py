#! -*- coding: utf-8 -*-

import sys
import six
import collections
from shopwave.utils import ShopwaveDatetime

# TODO: 
# - override __getattr__ for BaseField


class BaseField(object):
    """
    Parameters
    ----------
    blank : bool
        If False, corresponding attribute will always be set on model
        instantiation, using default() if no value provided. If True, attribute
        will not be set if no value is provided.

    Attributes
    ---------
    attrname : string
        Attribute name in model linking to this field instance.
    """
    _is_basefield = True
    def __init__(self, *args, **kwargs):
        self._primary_key = kwargs.pop('primary_key', False)
        self.alt_name = kwargs.pop('alt_name', None)
        self.alias = kwargs.pop('alias', [])
        self.blank = kwargs.pop('blank', False)
        if self._primary_key and 'id' not in self.alias:
            self.alias.append('id')

    def __repr__(self):
        u = getattr(self, 'attrname', '')
        if not u: u = getattr(self, 'attrname', '')
        if not u: u = getattr(self, 'alias', '')
        if hasattr(self, 'model'):
            m = "%s." % self.get_model().__class__.__name__ 
        else:
            m = ''
        return str('<%s: %s%s>' % (self.__class__.__name__, m, u))

    def default(self):
        return "DEFAULT"

    def parse_value(self, val):
        if val is not None and val is not self.default():
            try:
                new_val = self._parse_value(val)
            except ValueError as e:
                raise ValueError('Error in parsing value for %s. %s' %\
                                (self.__repr__(), str(e)))
        else:
            new_val = self.default()
        return new_val

    def set_model(self, model):
        self.model = model

    def get_model(self):
        return getattr(self, 'model', None)

class IntField(BaseField):
    def _parse_value(self, value):
        return int(value)

class FloatField(BaseField):
    def _parse_value(self, value):
        return float(value)

class CharField(BaseField):
    def _parse_value(self, value):
        return str(value)

class DateTimeField(BaseField):
    def _parse_value(self, value):
        return ShopwaveDatetime(value)

class Reference(BaseField):
    def __init__(self, *args, **kwargs):
        """
        Parameters
        ----------
        references : class derived from shopwave.models.Model
        attrname : list of strings, optional
            If for each id only one value is provided, specify attrname as
            corresponding attribute name. If for each id a dict of values is
            provided, dont specify this value.
        """
        self._RefModel = kwargs.pop('references')
        self.ref_attrname = kwargs.pop('attrname', None)
        super().__init__(*args, **kwargs)

    def default(self):
        return []

    def get_ref_model(self):
        RefModel = self._RefModel
        models = sys.modules[self.get_model().__module__]
        if isinstance(RefModel, six.string_types):
            RefModelName = RefModel
            RefModel = getattr(models, RefModelName)
        return RefModel

    def _parse_value(self, data):
        """
        Data can take three forms:
            1. dict of id as key and value of some other attr, 
                e.g. {'1234212': 'Coffee', '12421': 'Cake'}
            2. dict of id as key and value some other dict of key:value pairs for
                that model instance.
            3. list of ids, e.g. ['123124', '214221', '241233']
        """
        result = list()
        RefModel = self.get_ref_model()
        if self.ref_attrname:
            # Datatype 1.) dict of id as key -> other attr. value as value.
            for idNr in data:
                model = RefModel
                model.id = idNr
                setattr(model, self.ref_attrname, data[idNr])
                result.append(model)

        elif isinstance(data, collections.Mapping):
            # Datatype 2.) dict of id as key -> dict of attr.key->attr.val.
            for idNr in data:
                model = RefModel(data=data[idNr])
                model.id = idNr
                result.append(model)
        else:
            # Datatype 3.) list of ids.
            for idNr in data:
                model = RefModel(id=idNr)

        return result




        


        
