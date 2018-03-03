#!/usr/bin/env python3
#

import psycopg2


def get_most_popular_posts():
    """Return the 3 most popular articles"""

    db = psycopg2.connect("dbname=news")

    cursor = db.cursor()

    # sql to be run
    sql = ("select articles.title as title, count(*) as num "
           "from articles join "
           "(select substring(path from 10 for 30) as logpath from log) as l "
           "on articles.slug = l.logpath "
           "group by articles.title order by num desc "
           "limit 3")

    # sql execution
    cursor.execute(sql)
    rows = cursor.fetchall()

    # housekeeping
    db.close

    return rows


def get_most_popular_authors():
    """Return a summary of authors' views in descending order"""

    #  using the psycopg2 module to get connection to news db
    db = psycopg2.connect("dbname=news")
    cursor = db.cursor()

    # sql to be executed
    sql = ("select authors.name, count(*) as num from authors, "
           "articles, log "
           "where authors.id = articles.author and "
           "substring(log.path from 10 for 30) = articles.slug "
           "group by authors.name "
           "order by num desc;")

    # sql execution
    cursor.execute(sql)
    rows = cursor.fetchall()

    # housekeeping
    db.close

    return rows


def get_errors():
    """Return average requests that errored out per day"""

    #  using the psycopg2 module to get connection to news db
    db = psycopg2.connect("dbname=news")
    cursor = db.cursor()

    # sql to be executed
    sql = ("select a.day as day, "
           "to_char(a.errors/a.requests*100.00,'FM999999999.00') "
           "as average_errors from "
           "(select errors_view.day as day, errors_view.num_errors as errors, "
           "requests_view.num_requests as requests "
           "from "
           "(select day, cast(count(*) as float) as num_errors from "
           "(select to_char(time, 'FMMonth DD, YYYY') as day, "
           "status as status "
           "from log where log.status != '200 OK') as error_days "
           "group by day) as errors_view "
           "join "
           "(select day, cast(count(*) as float) as num_requests from "
           "(select to_char(time, 'FMMonth DD, YYYY') as day, "
           "status as status from log) as total_requests "
           "group by day) "
           "as requests_view "
           "on errors_view.day = requests_view.day) as a "
           "where a.errors/a.requests*100.00 > 1; ")

    # sql execution
    cursor.execute(sql)
    rows = cursor.fetchall()

    # housekeeping
    db.close

    return rows
