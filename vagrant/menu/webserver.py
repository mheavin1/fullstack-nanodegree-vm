# add the shebang or whatever here

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

#  import common gateway interface
import cgi

# imports related to DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#  the Restaurant, Base and MenuItem are imported from the database_setup.py file created in lesson 1
from database_setup import Restaurant, Base, MenuItem

#  create a session and connect to db
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


#  this class inherits from BaseHTTPRequestHandler... so it extends BaseHTTPRequestHandler
class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print("here we are in the do_GET")

            if self.path.endswith("/delete"):
                print("here is the path value")
                print(self.path)

                # pull the restaurant id out of the path
               
                restaurant_id = self.path.split('/')[2]
                print(restaurant_id)

                restaurant_id_int = int(restaurant_id)
                print("printing restaurant_id_int")
                print(restaurant_id_int)

                print("trying to get the restaruant")
                restaurant_to_update = session.query(Restaurant).filter_by(id = restaurant_id_int).one()

                action = "/restaurants/%s" %restaurant_id
                
                action += "/delete"

                #  path will be a value like: /restaurant/1/edit
                #  where the number 1 is the id of the restaurant to edit, need to pull that value out
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<div>Are you sure you want to delete the restaurant: </div>"
                output += restaurant_to_update.name
                output += "<div></br></div>"

                output += "<form method='POST' enctype='multipart/form-data' "
                output += "action ='%s" %action
                #output += action
                output += "'>"\
                          "<input type='submit' "\
                          "value = 'Delete'> </form>"
                
                      #"action ='/restaurants/edit'>"\
                      #"<input name='restaurant' type='text' ><input type='submit' "\
                      #"value = 'Submit'> </form>"


                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                print("here is the path value")
                print(self.path)

                # pull the restaurant id out of the path
                pathtosplit = self.path
                path_elements = pathtosplit.split('/')
                restaurant_id = path_elements[2]
                print(restaurant_id)

                action = "/restaurants/"
                action += restaurant_id
                action += "/edit"

                #  path will be a value like: /restaurant/1/edit
                #  where the number 1 is the id of the restaurant to edit, need to pull that value out
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<div>Change Restaurant Name</div>"
                output += "<div></br></div>"

                output += "<form method='POST' enctype='multipart/form-data' "
                output += "action ='"
                output += action
                output += "'>"\
                          "<input name='restaurant' type='text' ><input type='submit' "\
                          "value = 'Submit'> </form>"
                
                      #"action ='/restaurants/edit'>"\
                      #"<input name='restaurant' type='text' ><input type='submit' "\
                      #"value = 'Submit'> </form>"


                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
                

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<div>Make a New Restaurant</div>"
                output += "<div></br></div>"

                output += "<form method='POST' enctype='multipart/form-data' "\
                      "action ='/restaurants/new'>"\
                      "<input name='restaurant' type='text' ><input type='submit' "\
                      "value = 'Submit'> </form>"


                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
                
            
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""

                # make a new restaurant link
                output += "<div><a href = '/restaurants/new' >Make a New Restaurant</a></div>"
                output += "<div></br></div>"

                for restaurant in restaurants:
                    output += "<div>"
                    output += restaurant.name
                    output += "</div>"
                    
                    print(restaurant.name)
                    print('\n')

                    restaurant_name = restaurant.name
                    restaurant_id = restaurant.id

                    edit_link = "/restaurant/"
                    edit_link +=str(restaurant.id)
                    edit_link += "/edit"
                    
                    delete_link = "restaurant/"
                    delete_link += str(restaurant.id)
                    delete_link += "/delete"

                    output += "<div>"
                    output+= "'<a href = '"
                    output+= edit_link
                    output+= "'>Edit</a>'"
                    output += "</div>"

                    output += "<div>"
                    output+= "'<a href = '"
                    output+= delete_link
                    output+= "'>Delete</a>'"
                    output += "</div>"

                    output += "<div></br></div>"
               
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
                
                
            
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "Hello!"
                
                output += "<form method='POST' enctype='multipart/form-data' "\
                      "action ='/hello'><h2>What would you like me to say?</h2>"\
                      "<input name='message' type='text' ><input type='submit' "\
                      "value = 'Submit'> </form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "&#161Hola <a href = '/hello' >Back To Hello</a></body></html>"
                output += "<form method='POST' enctype='multipart/form-data' "\
                      "action ='/hello'><h2>What would you like me to say?</h2>"\
                      "<input name='message' type='text' ><input type='submit' "\
                      "value = 'Submit'> </form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)


    def do_POST(self):
        try:
            print("from the do_POST")

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    restaurant_content = fields.get('restaurant')
                    restaurant_name = restaurant_content[0]
                    print(restaurant_name)

                    # db work
                    restaurant1 = Restaurant(name=restaurant_name)
                    session.add(restaurant1)
                    session.commit()
                    print("db work completed")

                    # one way to do it, we could just redirect back to restaurants
                    self.send_response(301)
                    self.send_header('Content-type',  'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                #return


            if self.path.endswith("/delete"):
                print("made it to the post, delete code")
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    
                

                    print("here is the path value")
                    print(self.path)

                    # pull the restaurant id out of the path
                    pathtosplit = self.path
                    path_elements = pathtosplit.split('/')
                    restaurant_id = path_elements[2]
                    print(restaurant_id)


                    # db work
                    
                    #restaurant1 = Restaurant(name=restaurant_name)
                    #session.add(restaurant1)
                    #session.commit()

                    restaurant_id_int = int(restaurant_id)
                    print("printing restaurant_id_int")
                    print(restaurant_id_int)

                    print("trying to get the restaruant")
                    restaurant_to_update = session.query(Restaurant).filter_by(id = restaurant_id_int).one()
                    print(restaurant_to_update.name)

                    
                    session.delete(restaurant_to_update)
                    session.commit()
                    
                    print("db work completed")

                    # one way to do it, we could just redirect back to restaurants
                    self.send_response(301)
                    self.send_header('Content-type',  'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    restaurant_content = fields.get('restaurant')
                    restaurant_name = restaurant_content[0]
                    print("printing restaurant name pulled from the post data:")
                    print(restaurant_name)

                    print("here is the path value")
                    print(self.path)

                    # pull the restaurant id out of the path
                    pathtosplit = self.path
                    path_elements = pathtosplit.split('/')
                    restaurant_id = path_elements[2]
                    print(restaurant_id)


                    # db work
                    
                    #restaurant1 = Restaurant(name=restaurant_name)
                    #session.add(restaurant1)
                    #session.commit()

                    restaurant_id_int = int(restaurant_id)
                    print("printing restaurant_id_int")
                    print(restaurant_id_int)

                    print("trying to get the restaruant")
                    restaurant_to_update = session.query(Restaurant).filter_by(id = restaurant_id_int).one()
                    print(restaurant_to_update.name)

                    restaurant_to_update.name = restaurant_name
                    session.add(restaurant_to_update)
                    session.commit()
                    
                    print("db work completed")

                    # one way to do it, we could just redirect back to restaurants
                    self.send_response(301)
                    self.send_header('Content-type',  'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            
##            self.send_response(301)
##            self.end_headers()
##
##            # ctype stands for content type
##            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
##            if ctype == 'multipart/form-data':
##                fields=cgi.parse_multipart(self.rfile, pdict)
##                restaurant_content = fields.get('restaurant')
##                restaurant_name = restaurant_content[0]
##                print(restaurant_name)
##
##       
##            restaurant1 = Restaurant(name=restaurant_name)
##            session.add(restaurant1)
##            session.commit()
##
##            print("now building the output")
##            output = ""
##            output += "<html><body>"
##            output += " <h2> Name of new restaurant: </h2>"
##            output += "<h1> %s </h1>" % restaurant_name
##            output += "</br>"
##            #output += "<h1> %s </h1>" % message
##            output += "</br>"
##            output += "<div><a href = '/restaurants' >View the Restaurants</a></div>"
##            output += "</br>"
##            
##            #output += "<form method='POST' enctype='multipart/form-data' "\
##            #          "action ='/hello'><h2>What would you like me to say?</h2>"\
##            #          "<input name='message' type='text' ><input type='submit' "\
##             #         "value = 'Submit'> </form>"
##             
##            output += "</body></html>"
##
##            self.wfile.write(output)
##            print output
                       
            
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()




if __name__ == '__main__':
    main()
