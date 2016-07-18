# TodayProject

# Running
Run local server with following line code:
runserver --settings TodayProject.paris_settings

access it at:
127.0.0.1:8000

# Organization
The project concerns different topics ("thèmes" in french, such as 'catho', 'jobs') for differents cities.
A single website is dedicated to each city, using django sites framework.
Each topic concerns different categories ("catégories" in french)

# Architecture
The project is currently divided in 6 different applications (folders)
- TodayProject folder contains all files related to the whole project: settings, main urls,...
- Core folder contains everything that is not specific to one topic (CGV, contact, 'qui sommes nous'...)
- connection folder contains everything related to connexion process
- topic folder is an abstract application that gives events depending on the url: if the url is paris.enjoytoday.fr/catho,
the current topic is catho, and the events served will only be catho events. The folders catho and jobs will contain specific
views and request that will overwrite Topic's classes (that are considered as 'standard features')
- crud folder contains everything related to Creation, Reading, Updating and Delation of events
- location contains everything related to location stuff
