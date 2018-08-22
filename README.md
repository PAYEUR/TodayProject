# TodayProject

## Description
This source code refers to a collaborative website developped under Django 1.9 and Python 2.7
The website aims to promote spiritual events such as talks, concerts or prayers in France.
The website offers the possibility for each registred user to promote events on his own.

You can access the online version at https://enjoytoday.payeur.eu

This website is still under development.

## Installation
The following source code runs under Python 2.7 (preferably under virtualenv)
(in a virtualenv)
pip install -r requirements.txt

## Running (development environment)
runserver --settings TodayProject.settings

access it at:
127.0.0.1:8000

## Architecture
The project is currently divided in 10 different folders

### Applications:
- TodayProject folder contains all settings files: settings, wsgi file, urls,...
- Core folder contains everything that is not specific to one topic (most of static pagees)
- connection folder contains everything related to connexion process
- topic folder is the model application related to events structure and management
- crud folder contains everything related to Creation, Reading, Updating and Delation of events
- location contains everything related to where events take place (not much for the moment)

### Static content:
- draft contains bunch of unused code
- media contains images uploaded from users
- fixtures contains fixtures files for tests
- widget contains js/jquery code related to the specific widgets of the website
