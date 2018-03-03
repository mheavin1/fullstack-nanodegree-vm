#!/usr/bin/env python3
#
# Display log analysis

from flask import Flask, request, redirect, url_for

from reporting_db import get_most_popular_posts
from reporting_db import get_most_popular_authors
from reporting_db import get_errors


app = Flask(__name__)

# HTML template for the most popular posts page
HTML_WRAP_MOST_POPULAR_POSTS = '''\
<!DOCTYPE html>
<html>
  <head>
    <title>News Reporting Tool</title>
    <style>
      h1 { text-align: center; }
      div.summary_line { text-align: center;
                 padding: 10px 10px;}
    </style>
  </head>
  <body>
    <h1>Most Popular Posts</h1>

    <!-- summary lines will go here -->
%s
  </body>
</html>
'''

# HTML template for the most popular author
HTML_WRAP_MOST_POPULAR_AUTHORS = '''\
<!DOCTYPE html>
<html>
  <head>
    <title>News Reporting Tool</title>
    <style>
      h1 { text-align: center; }
      div.summary_line { text-align: center;
                 padding: 10px 10px;}
    </style>
  </head>
  <body>
    <h1>Most Popular Authors</h1>

    <!-- summary lines will go here -->
%s
  </body>
</html>
'''

# HTML template for days where greater than 1% of requests errored
HTML_WRAP_ERRORS = '''\
<!DOCTYPE html>
<html>
  <head>
    <title>News Reporting Tool</title>
    <style>
      h1 { text-align: center; }
      div.summary_line { text-align: center;
                 padding: 10px 10px;}
    </style>
  </head>
  <body>
    <h1>Days where greater than 1 percent of the requests were errors</h1>

    <!-- summary lines will go here -->
%s
  </body>
</html>
'''

# HTML template for summary lines
SUMMARY_LINES = '''\
    <div class=summary_line>%s - %s  views</div>
'''

# HTML template for summary lines
SUMMARY_LINES_ERRORS = '''\
    <div class=summary_line>%s - %s%s errors</div>
'''


# route used to display the most popular posts
@app.route('/topviews', methods=['GET'])
def posts_summary():
    '''Displays the most popular posts.'''
    posts = "".join(SUMMARY_LINES % (title, num) for title,
                    num in get_most_popular_posts())
    html = HTML_WRAP_MOST_POPULAR_POSTS % posts
    return html


# route used to display most popular authors
@app.route('/topauthors', methods=['GET'])
def authors_summary():
    '''Displays the most popular authors.'''
    posts = "".join(SUMMARY_LINES % (title, num) for title,
                    num in get_most_popular_authors())
    html = HTML_WRAP_MOST_POPULAR_AUTHORS % posts
    return html


# route used to display days with high number of errors
@app.route('/errors', methods=['GET'])
def errors_summary():
    '''Displays days where greater than 1% of requests errored out.'''
    posts = "".join(SUMMARY_LINES_ERRORS % (title, num, '%') for title,
                    num in get_errors())
    html = HTML_WRAP_ERRORS % posts
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
