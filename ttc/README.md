# kron

These scripts needs to run every day. 
You can cofigure the scripts with the config file.

## Teveclub

Teach and feed a virtual camel on teveclub.hu.

Requirements:
- feed, add water
- teach
- if not success: send an alert
- every 7 days send a notif that the camel is sill alive


## Ncore login
 in progress

 Requirements:
 - Just log-in to ncore every day

## Strava sync
inprogress

Requirements:
- get data from Strava
- get data from Fitbit
- store data in a database
- sync with Fitbit to Strava and later Runkeeper
  

#### Config file

```
{
    "teveclub": {
        "username": "USER",
        "password": "PASS"
    },
    "ncore": {},
    "email": {
        "default_subject": "Kron notification",
        "from": "me@gmail.com",
        "to": "me@gmail.com",
        "smtp": "smtp.gmail.com",
        "username": "me@gmail.com",
        "password": "APP_PASS",
        "port": 465
    }
}
```


### To AWS

ssm role add