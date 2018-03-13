from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Making an API endpoint (GET Request)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


# Making an API endpoint to return menu data for a specific restaurant (GET Request)
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id=menu_id).all()
    
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):

    #  http://localhost:5000/restaurants/3/
    
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    
    new_menu_link = url_for('newMenuItem', restaurant_id=restaurant.id)
    
    
    #  code here that uses the html template,
    #  supplies the template withe the restaurant and items objects
    return render_template('menu.html', restaurant=restaurant, items=items,
                           new_menu_link=new_menu_link)



# Task 1: Create route for newMenuItem function here

@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'],restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created")
        return redirect(url_for('restaurantMenu',restaurant_id = restaurant_id))
    
    else:
        return render_template('newmenuitem.html', restaurant_id = restaurant_id, restaurant = restaurant)

# Task 2: Create route for editMenuItem function here


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    
    editItem = session.query(MenuItem).filter_by(id=menu_id).one()
    
    if request.method == 'POST':
        
        editItem.name = request.form['name']
        session.add(editItem)
        session.commit()
        flash("menu item edited")
        return redirect(url_for('restaurantMenu',restaurant_id = restaurant_id))
        
    else:
        return render_template('editmenuitem.html', menu_id = menu_id, restaurant_id = restaurant_id, menu_item_name = editItem.name)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):

    
    if request.method == 'POST':
        session.query(MenuItem).filter_by(id=menu_id).delete()
        session.commit()
        flash("new menu item deleted")
        return redirect(url_for('restaurantMenu',restaurant_id = restaurant_id))
    
    else:
        deleteItem = session.query(MenuItem).filter_by(id=menu_id).one()
        return render_template('deletemenuitem.html', i = deleteItem, restaurant_id = restaurant_id, menu_id=menu_id)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
