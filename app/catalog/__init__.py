from flask import Blueprint


catalog = Blueprint('catalog', __name__, template_folder='templates')

from views import create_category

if __name__ == '__main__':
    create_category()
