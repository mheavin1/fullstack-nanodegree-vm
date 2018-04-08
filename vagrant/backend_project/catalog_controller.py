from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from collections import OrderedDict

app = Flask(__name__)

#  declaring the CLIENT_ID using the json
#  file downloaded from google+
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///sportscatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# items json
@app.route('/items/json')
def itmesJSON():

    items = session.query(Item).all()
    return jsonify(Item=[i.serialize for i in items])

# items json
@app.route('/item/<int:item_id>/json')
def itemJSON(item_id):

    # get the item
    item = session.query(Item).filter_by(
        id=item_id).first()
    return jsonify(Item=[item.serialize])


# categories json
@app.route('/categories/json')
def categoriesJSON():

    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])


# categories with their items
@app.route('/fullCatalog/json')
def categoriesItemsJSON():

    # get all categories
    categories = session.query(Category).all()

    # catalog dictionary
    catalog = {}

    # loop over categories to build the list
    categories_list = []
    for category in categories:
        # loop over all the items for current category
        items = session.query(Item).filter_by(cat_id=category.id).all()
        items_list = []
        for item in items:
            item_data = {'id': item.id,
                         'description': item.description,
                         'title': item.title}
            items_list.append(item_data)

        # build the final json object for an individual category
        category_json_object = {'id': category.id, 'name': category.name,
                                'Items': items_list}

        # add category json object the categories list
        categories_list.append(category_json_object)

    # create final dictionary
    output_catalog = {'Categories': categories_list}

    return jsonify(output_catalog)


# homepage
@app.route('/')
@app.route('/homepage')
def homePage():

    # get all categories
    categories = session.query(Category).all()

    # get latest items
    items = session.query(Item).order_by(
        desc(Item.time_created)).limit(12).all()

    return render_template('index.html', categories=categories,
                           items=items)


# show items for a specific category
@app.route('/catalog/<string:category_name>/items')
def itemsForCategory(category_name):
    # strip out the pluses and replaces with spaces
    # so that names with spaces will work
    new_category_name = category_name.replace("+", " ")

    # get the category for which we need to display items
    category = session.query(Category).filter_by(
        name=new_category_name).one()

    # get all categories to display on sidebar
    categories = session.query(Category).all()

    # get items associated with the category
    items = session.query(Item).filter_by(cat_id=category.id).all()

    # count of number of items for this category
    item_count = len(items)

    return render_template('categoryitems.html',
                           categories=categories, items=items,
                           category=category, item_count=item_count)


# show item information
@app.route('/catalog/<string:category_name>/<string:item_title>')
def itemInfo(category_name, item_title):

    # strip out the pluses and replaces with spaces
    # so that names with spaces will work
    new_item_title = item_title.replace("+", " ")
    new_category_name = category_name.replace("+", " ")

    # get the category for which we need to display items
    category = session.query(Category).filter_by(
        name=new_category_name).one()

    # get the item
    item = session.query(Item).filter_by(
        cat_id=category.id, title=new_item_title).first()

    print(item.user_id)

    # this method hits DB and gets a user
    item_owner = getUserInfo(item.user_id)

    if 'username' not in login_session or (
        'user_id' not in login_session) or (
            item_owner is None) or (
                item_owner.id != login_session['user_id']):
        print("rendering public page")
        return render_template('iteminfo.html',
                               item=item, category_id=category.id)
    else:
        print("rendering private page")
        return render_template('iteminfo_loggedin.html',
                               item=item, category_id=category.id)


# edit an item
@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):

    # if user isn't logged in redirect to login
    if 'username' not in login_session:
        return redirect('/login')

    # to render the edit item page,
    # all category names and id's to allow user to
    # select a new category, in a ordered collection
    # and i need the item to edit

    # get the item
    item = session.query(Item).filter_by(id=item_id).one()

    # check if has authorization
    if item.user_id != login_session['user_id']:

        return ("<script> function myfunction() "
                "{alert('You are not authorized to delete"
                " this item');}</script><body onload='myfunction()''>")

    # get all categories
    categories = session.query(Category).all()

    # i need an ordered dictonary so categories
    # display in the drop down in ascending order,
    # so i'm using OrderedDict
    cat_list = []
    for cat in categories:
        cat_dict_in_list = (cat.id, cat.name)
        cat_list.append(cat_dict_in_list)

    cat_dict = OrderedDict(cat_list)

    # process the form if POST
    if request.method == 'POST':
        print("post start")

        new_title = request.form['item_title']
        if new_title:
            print("got item_title")
            print(item.title)
            item.title = new_title

        new_description = request.form['description']
        if new_description:
            item.description = new_description
            print("got description")
            print(item.description)

        new_catg_id = request.form['new_category_id']
        if new_catg_id:
            print("got the new cat id")
            category = session.query(Category).filter_by(
                id=new_catg_id).one()
            print("got the new category object from db")
            print(category.name)
            item.category = category
            print("updated the item.category")

        session.add(item)
        session.commit()
        print("after the commit")
        flash("item: %s updated" % item.title)
        print("attempting to call homePage")
        # redirect back to home page
        return redirect('/homepage')

    else:
        return render_template('edititem.html', item=item,
                               cat_dict=cat_dict)


# delete an item
@app.route('/catalog/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):

    # if user isn't logged in redirect to login
    if 'username' not in login_session:
        return redirect('/login')

    # call DB, get the item
    print("query db for item with id = %s" % item_id)
    item = session.query(Item).filter_by(id=item_id).one()

    # check if user has authorization
    if item.user_id != login_session['user_id']:

        return ("<script> function myfunction() "
                "{alert('You are not authorized to delete "
                "this item');}</script><body onload='myfunction()''>")

    # process the post
    if request.method == 'POST':
        # get the item to delete

        item_title = item.title
        print("Item to Delete:")
        print(item.title)
        session.delete(item)
        session.commit()
        print("after the commit")
        flash("item: %s deleted" % item_title)
        print("attempting to call homePage")
        # redirect back to home page
        return redirect('/homepage')
    else:
        return render_template('deleteitem.html', item=item)


# show item information
@app.route('/catalog/new/item', methods=['GET', 'POST'])
def newItem():
    # if user isn't logged in redirect to login
    if 'username' not in login_session:
        return redirect('/login')

    # get the user who is making this item
    # for the relationship between user and item
    user_id = login_session['user_id']
    current_user = getUserInfo(user_id)
    print("user_id making the item: %s" % current_user.id)

    # get all categories
    categories = session.query(Category).all()

    # i need an ordered dictonary so categories
    # display in the drop down in ascending order,
    # so i'm using OrderedDict
    cat_list = []
    for cat in categories:
        cat_dict_in_list = (cat.id, cat.name)
        cat_list.append(cat_dict_in_list)

    cat_dict = OrderedDict(cat_list)

    if request.method == 'POST':

        # used to determine if error was made
        error = False

        new_title = request.form['item_title']
        if new_title:
            print("got item_title")
            print(new_title)
        else:
            # error, title required
            flash("item title is required")
            error = True

        new_description = request.form['description']
        if new_description:
            print("got description")
            print(new_description)
        else:
            # error
            flash("item description is required")
            error = True

        new_catg_id = request.form['new_category_id']
        if new_catg_id:
            print("got the new cat id")
            new_category = session.query(
                Category).filter_by(id=new_catg_id).one()
            print("got the new category object from db")
            print(new_category.name)
        else:
            # error
            flash("A category is required")
            error = True

        if error:
            return render_template(
                'newitem.html', cat_dict=cat_dict)

        item = Item(description=new_description,
                    title=new_title, category=new_category,
                    user=current_user)
        session.add(item)
        session.commit()
        print("commit completed")
        flash("The new item was created with item title: %s "
              % item.title)
        return redirect('/homepage')

    else:
        # to display the new item page,
        # i need a drop down list of categories

        return render_template('newitem.html', cat_dict=cat_dict)


# Create anti-forgery state token
#  hitting this route will return basically a session id,
#  each time you refresh this in your browser you'll get a new session id
#  the login.html template has code that will go out to google to authenticate
@app.route('/login')
def showLogin():
    # state is a random mix of uppercase letters and digits
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print("state:")
    print(state)
    # render the login template
    return render_template('login.html',  STATE=state,
                           client_id=CLIENT_ID)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    print("beginning gconnect function")

    #  so we created the state session using the
    #  imported login_session in the showLogin function,
    #  then in showLogin, we passed that state to the login.html
    #  now, login.html is passing that state back to us,
    #  and we are comparing to make sure it is the same

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameters'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code that came from google+
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid..
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # if there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(
            result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doens't match given user ID."
                       ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected'), 200)
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    print("about to load profile info into session")

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    print("loaded username, picture and email into session")

    #  Check if this user is in the database, and if not, add them
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    print("setting user_id into session")
    print(user_id)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; '
               'height: 300px;border-radius: '
               '150px;-webkit-border-radius: '
               '150px;-moz-border-radius: 150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT, IS IT GOOGLE OR FACEBOOK, ACT ACCORDINGLY
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()

    return redirect('/homepage')


# GOOGLE DISCONNECT - Revoke a current user's token
# and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    print("logging out google")
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access token is none'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("you have been successfully logged out")
        return response
    else:
        response = make_response(json.dumps(
            'Fialed to revoke token for user.', 400))
        response.headers['Content-Type'] = 'application/json'
        flash("Sorry, we had a problem logging you out.")
        return response


# Facebook function
@app.route('/fbconnect', methods=['POST'])
def fbconnect():

    # state was originally created in the
    # showLogin function using plain ole python,
    # state was passed to the login page,
    # the login page has now passed it back, and we verify it now
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # this token came from facebook when the user logged in via facebook
    access_token = request.data
    print("access token received %s " % access_token)

    # exchange client token for long-lived server-side token with GET,
    # which means calling Facebook with the token passed here by the client
    # the client calls facebook, gets a token and passes the token here,
    # then here, we call facebook and get a long lived token
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    print(app_id)
    print(app_secret)
    print(access_token)

    url = ('https://graph.facebook.com/v2.12/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    print(data)
    token = 'access_token=' + data['access_token']
    # see: https://discussions.udacity.com/t/
    #   issues-with-facebook-oauth-access-token/233840?source_topic_id=174342

    # Use token to get user info from API
    # make API call with new token
    url = ('https://graph.facebook.com/v2.12/me?%s&fields=name,id,'
           'email,picture' % token)

    # new: put the "picture" here, it is now
    # part of the default "public_profile"

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['picture'] = data['picture']["data"]["url"]
    login_session['access_token'] = access_token

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1><img src="'
    output += login_session['picture']
    output += ' ">'

    flash("Now logged in as %s" % login_session['username'])
    return output


# Facebook disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    print("logging out facebook")
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['facebook_id']
    return "you have been logged out"


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
