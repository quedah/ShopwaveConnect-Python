


# You need to provide these values.
CLIENT_ID =         '<YOUR CLIENT ID HERE>'
CLIENT_SECRET =     '<YOUR CLIENT SECRED HERE>'

REDIS_STORE = {
    'host': 'localhost',
    'port': 6379
}

REDIRECT_URI =      "<YOUR REDIRECT URI HERE>"



AUTH_BASE_URL =    "http://secure.beta.merchantstack.com/"
API_BASE_URL =      "http://api.staging.merchantstack.com/"
AUTH_URI =          "oauth/authorize"
OAUTH_BASE_URL =    "http://secure.beta.merchantstack.com/"
TOKEN_URI =         OAUTH_BASE_URL + "oauth/token"


ACCESS_TYPE =       "online"
RESPONSE_TYPE =     "code"

LOGOUT_URI =        "logout"

USER_AGENT = 'ShopwaveConnector-0.1'
X_ACCEPT_VERSION = '0.6'

AVAILABLE_SCOPES = [  
            "user", "application", "merchant","store", "product", "category",
            "basket", "promotion", "log", "supplierStore", "supplier",
            "invoice", "stock"]

# date format used by shopwave API
# See https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

OBJECT_LIST = (
    'Category',
    'Merchant',
    'Product',
    'Report_Basket',
    'Store',
    'Status',
    'Application',
    'Category',
    'Employee',
    'Invoice',
    'Log',
    'Product_Component',
    'Promotion',
    'Stock_Reconcile',
    'Supplier',
    'Uploader',
    'User',
)
