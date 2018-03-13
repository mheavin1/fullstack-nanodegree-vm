from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/hello')
def HelloWorld():
    
    restaurant = session.query(Restaurant).filter_by(id = 3).one()

    print(restaurant.name)
    print(restaurant.id)

    output = ''
    
    menuitems = session.query(MenuItem).all()

    for m in menuitems:
        #print(m.name)
        #print(m.id)
        #print(m.restaurant_id)
        #print("-----------------")

        output += m.name
        output += '</br>'
        output += m.price
        output += '</br>'
        output += m.description
        output += '</br>'
        output += '</br>'
    
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    print(items)


    output += '</br>---------------------------------------------------------'
    
    for i in items:
        output += i.name
        output += '</br>'
        output += i.price
        output += '</br>'
        output += i.description
        output += '</br>'
        output += '</br>'
    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
