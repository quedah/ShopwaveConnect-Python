#! -*- coding: utf-8 -*-

import six
import json
from shopwave import fields

class ModelMetaData:
    """
    Holds meta information for each Model instance, saved as '_meta' attribute
    of that instance.
    """
    def __init__(self, model_name=None, fields=[]):
        self._fields = {}
        self._alias = {}
        self._primary_field = None
        self.model_name = model_name
        for f in fields:    
            self.add_field(f)

    def get_field_names(self):
        """ Get list of all field names and aliases
        """
        names = set()
        names.update(list(self._fields.keys())) 
        names.update(list(self._alias.keys()))
        names.update(['id'])
        return names

    def get_fields(self):
        """ Get list of all fields.
        """
        return list(self._fields.values())

    def get_field(self, key):
        """ Get field with attrname or an alias matching key.
        """
        if key == 'id':
            return self.get_primary_field()
        elif key in self._fields:
            return self._fields[key]
        elif key in self._alias:
            return self._fields[self._alias[key]]
        raise KeyError("No field with '%s' as name or alias can be found." % key)

    def get_primary_field(self):
        return self._primary_field

    def add_field(self, field):
        if field.attrname == 'id':
            field._primary_key = True

        if field._primary_key:
            if self._primary_field is not None:
                raise ValueError('Only one field can be primary key in '+\
                                 'model %s.' % (model_name))
            else:
                self._primary_field = field

        for alias_name in field.alias:
            self._alias[alias_name] = field.attrname

        self._fields[field.attrname] = field

    def set_model(self, model):
        self.model = model
        for field in self.get_fields():
            field.set_model(model)


class ModelBase(type):
    """
    Metaclass for Model.
    """
    def __new__(cls, name, bases, attrs):
        meta = ModelMetaData(model_name=name)
        new_attrs = dict()
        for k, v in attrs.items():
            # Setting default values for all specified fields in model that are
            # not set to blank.
            if hasattr(v, '_is_basefield'): 
                if not v.blank:     new_attrs[k] = v.default()
                v.attrname = k
                meta.add_field(v)
            else:
                new_attrs[k] = v
        new_attrs['_meta'] = meta
        return super().__new__(cls, name, bases, new_attrs)

    def _validate(self):
        return True


class Model(metaclass=ModelBase):
    def __init__(self, **kwargs):
        """
        If json and kwargs are specified, json value will take precedence.

        Primary key will correspond to object Shopwave id. Only one field can be
        designated as primary key and has to correspond to the Shopwave primary
        key. If a field named 'id' is added, that field will be automatically
        designated as primary key.

        Parameters
        ----------
        json : string, JSON, optional
            JSON data as returned from shopwave API
        data : dict, optional 
            Same as json, but converted to python dict.
        """
        super().__init__()
        self._meta.set_model(self)
        if 'json' in kwargs:
            # Create instance from json.
            construct_from_json = True
            json_data = kwargs.pop('json')
            kwargs.update(json.loads(json_data))

        if 'data' in kwargs:
            data = kwargs.pop('data')
            kwargs.update(data)

        for name in self._meta.get_field_names():
            value = kwargs.pop(name, None)
            if value is not None:       setattr(self, name, value)

        # >>>
        """
        for f in self._meta.get_fields():
            attrname = f.attrname

            value = kwargs.pop(attrname, None)
            if value is not None:
                setattr(self, attrname, value)
        """
         # <<<

        if kwargs:
            raise TypeError(
                'Instantiating %s: %s is an invalid keyword argument for this function.' 
                 % (self.__class__, list(kwargs)[0])
            )

        # Check attribute names and fields alt_names for fields to use as
        # representative values for each instance of Model.
        self._meta._name_attr = ''
        for name_attr in ['name', 'title', 'details']:
            if hasattr(self, name_attr): 
                self._meta._name_attr = name_attr
                break
            for field in self._meta.get_fields():
                if field.alt_name and field.alt_name.lower() == name_attr:
                    self._meta._name_attr = field.attrname
                    break

    def __setattr__(self, k, v):
        field = self._meta.get_field(k)
        attrname = field.attrname
        parsed_value = field.parse_value(v)
        super().__setattr__(attrname, parsed_value)

    def __repr__(self):
        u = getattr(self, self._meta._name_attr, self.__class__.__name__)
        return str('<%s: %s>' % (self.__class__.__name__, u))

    def __str__(self):
        if six.PY2 and hasattr(self, '__unicode__'):
            return str(self).encode('utf-8')
        return str('%s object' % self.__class__.__name__)

    def _from_json(self, json_data):
        data = json.loads(json_data) 
        fields = self._meta.get_fields()
        for f in fields:
            data.pop(f.attrname, f.default())

        if data:
            raise TypeError(
                '%s is an invalid json key for this function.' 
                 % list(data)[0]
            )


