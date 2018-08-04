# Smart Pump Backend

## Summary  
Smart Pump is an autonomous system which waters yours plants when you are not at home.

Smart Pump Backend is the back end component of this autonomous watering system. It is based on the [Django web application framework](https://www.djangoproject.com/) and [Bootstrap 4 CSS framework](https://getbootstrap.com/). It provides a HTTP REST API
for the clients in order to fetch all relevant information e.g. the duration of a pump cycle and the timespan between to cycles. The web application has also a built-in monitoring function and shows you the "health status" of your pump.   

## Disclaminer
**Smart Pump Backend contains NO USER AND DEVICE AUTHENTICATION at the moment. This will be implemented in the future.**

## Required Python Packages
### For Development & Testing (see pip/dev.pip)
* coverage
* Django
* django-bootstrap4
* django-tables2
* django-webtest
* django-jenkins
* pytest
* flake8
* pylint

### For Production Use (see pip/productive.pip)
* Django
* django-bootstrap4
* django-tables2


## Run Software (Development and Debug Mode)
```
git clone https://github.com/h3nr1-g/Smart-Pump-Backend.git
cd Smart-Pump-Backend
pip install -r pip/dev.pip
cd spb
python manage.py makemigrations api monitor && python migrate
python manage.py test --settings=spb.settings.dev && python manage.py runserver --settings=spb.settings.dev
```
