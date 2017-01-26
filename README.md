
ShopwaveConnect-Python
=====================

A Python API for accessing the [Shopwave](http://developer.merchantstack.com/shopwave/api/documentation) REST API. 

### Setup

Register your app with Shopwave [here](http://developer.merchantstack.com/app) and 
enter `CLIENT_ID` and `CLIENT_SECRET` in the **settings.py** file in the root directory. 
If you like you can use a Redis database to store your access and refresh tokens. Make sure
to specify `REDIS_STORE` as well in that case. 

You will need to request an access code and access & refresh tokens from the Shopwave API. 
Depending on your projects workflow, you may need to have a service for redirecting the 
Shopwave API to capture the access code. The script **app.py** in the root directory is an 
example of a basic [falcon](https://falconframework.org) server to do that.


### Authorisation & Authentication 

Before we can start communicating with the Shopwave API, we first need to get an 
authorisation code (see the previous section for an idea on how this might be
done) and pass this value to our Credentials instance:

```python
>>> # We can do this
>>> auth_code = '<My_Auth_Code>'
>>> cred = Credentials(authorization_code=auth_code)
>>>
>>> # We can also pass it into an already instantiated Credentials 
>>> # instance. This is equivalent
>>> cred = Credentials()
>>> # ... do some other stuff
>>> cred.verify(auth_code)
>>> # ... start communicating with Shopwave API
```

The important part is that this has to be done before any other calls to the
Shopwave API. If you have a redis server persistently running and redis host and
port specified in the settings.py file, you will not have to pass the
authorisation code again after this.

Once this is all done we can now get 
an authorised and authenticated Shopwave instance to talk to the Shopwave API

```python
>>> from shopwave import Shopwave, Credentials, Scope
>>>
>>> # Creating scope for our application. 
>>> scope = Scope(['user', 'application', 'product'])
>>> cred = Credentials(scope)
>>> sw = Shopwave(cred)
```
If no scope is provided, the Credentials instance will request access to all available
services.


### Usage 

All Shopwave API endpoints are accessible through this Shopwave instance. For example:

```python
>>> # Getting all products
>>> sw.product.all()
[<Product: Coffee>,
 <Product: Tea>,
 <Product: Chocolate Muffin>,
 <Product: Cheese Cake>]
>>> # Product is a derived class from shopwave.model and 
>>> # we can get and set all attributes like regular class
>>> # attributes:
>>> muffin = sw.product.get(103726)
>>> muffin.name 
'Chocolate Muffin'
>>> muffin.price
100.0
>>> muffin.price = 120.0
>>> muffin.price
120.0
>>> muffin.save()   # NEED TO IMPLEMENT SAVE!!
>>>
>>> # We can also get the raw response from the Shopwave server.
>>> # Getting all categories, with response json 
>>> # converted directly into python dict
>>> # i.e. not converting into shopwave.model instances
>>> sw.category.all(return_format_raw=True)
{'categories': {'8595': {'activeDate': '2017-01-09T16:49:58.000Z',
'deleteDate': None,
'id': 8595, 
'parentId': None,
'title': 'Drinks',
  'type': 0},
8644': {'activeDate': '2017-01-18T13:31:44.000Z'
...
...
```

## Converting Shopwave to Xero objects

### Constructing Xero Invoice from Shopwave API

Converting an instance from Shopwave's *report basket* endpoint (see documentation [here](http://developer.merchantstack.com/shopwave/api/documentation/report/basket/GET)) to Xero's *invoices*
API endpoing (see documentation [here](https://developer.xero.com/documentation/api/invoices)).

| Shopwave Basket Transaction                 | Xero Invoice                                   |
| --------------------------------------------|------------------------------------------------|
| tA (transaction amount)                     | AmountDue                                      |
| tA (transaction amount)                     | Total                                          |
| c  (basket completed date)                  | Date                                           |
| c  (basket completed date)                  | DueDate                                        |

In addition, the following values are being set in Xero Invoice

| Field Name                                  | Field Value                                    |
| --------------------------------------------|------------------------------------------------|
| CurrencyCode                                | *where do I get this from?*                    |
| Type                                        | ACCREC / ACCPAY *which one, when, how?*        |
| Contact                                     | *this is required, what to use?*               |
| LineAmountTypes                             | *exclusive usually used, what is right?*       |

### Constructing Xero Items

| Shopwave Product                            | Xero Item                                      |
| --------------------------------------------|------------------------------------------------|
| barcode *or id??*                           | Code                                           |
| name                                        | Name                                           |
| activeDate *derived from*                   | IsSold                                         |
| price                                       | UnitPrice                                      |


### Constructing Linked Transactions
Invoice Id and Item ID for instances created above can be used to generate a
Xero Linked Transaction.


