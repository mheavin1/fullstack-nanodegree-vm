#  News Reporting Tool readme file

This project creates a log analysis tool to pull different statistics from the news database.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


Unzip the contents of news_reporting_tool.zip into your vagrant shared directory

run python reporting_service.py

Access the reports by hitting the following urls:

following url shows most popular posts:
http://localhost:8000/topviews

following url shows days with more than 1percent of requuests were errors
http://localhost:8000/errors

following url shows most popular authors
http://localhost:8000/topauthors


### Prerequisites

Prequisites for this project include a Virtual Box installation, Vagrant installation and Vagrant file on your computer.

### Installing

Install Python from the Python Software Foundation's web site here:
https://www.python.org/downloads/

Example: install Python 3.6.4.

After installing Python add the install directory to your system's Path environment variable.

Install Virtual Box from here:
https://www.virtualbox.org/wiki/Downloads


Install Vagrant from here:
https://www.vagrantup.com/downloads.html


Get the appropriate vagrant file here:
https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f73b_vagrantfile/vagrantfile
Put this file into a new directory (folder) on your computer. 
Using your terminal, change directory (with the cd command) to that directory, 
then run vagrant up. You should see something like the picture below.
Then run vagrant ssh to login.

### Break down into end to end tests

The following url's will access the views:

following url shows most popular posts:
http://localhost:8000/topviews

following url shows days with more than 1percent of requuests were errors
http://localhost:8000/errors

following url shows most popular authors
http://localhost:8000/topauthors

Example: click the Toy Story image, the trailer for Toy Story will run in your browser as an imbedded Youtube video.

### And coding style tests

Coding style tests were completed with PEP8 online Check.

Example: http://pep8online.com/checkresult

## Deployment

Deploy on live system by cloning the git repository into your vagrant shared directory

## Built With

* [Python](https://www.python.org/downloads/) - The editor used

## Versioning

Version 1

## Authors

* Marc


