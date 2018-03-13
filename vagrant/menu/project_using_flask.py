from flask import Flask

# creating an object of type Flask, passing
# in tht default __name__ var this is passed to every python program
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#  create a session and connect to db
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# points to localhost:5000 and also localhost:5000/hello, these
# are called decorators in python
# stacked decorates do this:
# when root localhost:5000 is called, that hits the '/' route,
# then that hits '/hello' route'
@app.route('/')
@app.route('/hello')
def HelloWorld():

    print("starting the HelloWorld function")
    restaurant = session.query(Restaurant).first()

    # join using sqlalchemy
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    
    restaurants = session.query(Restaurant).all()
    for restaurant in restaurants:
        print(restaurant.name)
        
    
    print(items)
    
    output = ''

    print("beginning for loop")
    
    for i in items:
        output += i.name
        print("does name have a value?")
        print(i.name)
        output += '</br>'

    #  what we send to the browser, we return to sent to browser
    return output


        
    
    #return "Hello World"

# an application run by the python interpretor
# gets a name var that is equal to '__main__',
# while an imported python file gets a __name__ equal to the name of the file,
# so this line of code makes it only possible to run this file
# if it is ran by the python interpretor
# 
if __name__ == '__main__':
    # app.debug allows the server to reload changes to code
    app.debug = True

    # using host - 0.0.0.0 tells webserver on vagrant to listen on all public ip servers
    # this is needed to run on vagrant
    app.run(host = '0.0.0.0', port = 5000)
