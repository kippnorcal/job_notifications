# job_notifications
![Tests](https://github.com/kippnorcal/job_notifications/actions/workflows/tests.yml/badge.svg)

A simple package for sending ETL pipeline notifications to Slack.

## Dependencies
Using the MailGun API requires intalling the requestions library as well.

## Installation
Package can be installed through pip.
``````
pip install job-notificaitons
``````

## Set Up
The repo currently supports two ways to send notifications: 1) via MailGun API or 2) via Google SMTP email. Whichever method used needs to be declared when instantiating the package (see "Getting Started" below). Both methods require credentials. Credentials can be passed at time of instantiation or stored in a .env file. For security reasons, storing credentials in a .env file is teh recommended method.

### MailGun
Below are the credentials needed for using the MailGun API to be stored in an .evn file.
````
MG_URL=
MG_KEY=
````

### Google SMTP
Below are the credentials needed for using the MailGun API to be stored in an .evn file.
````
GMAIL_USER=
GMAIL_PASS=
````

### Additional Useful .env Variables
Here are come additional useful variables to store in your project's environment.
````
JOB_NAME=
TO_ADDRESS=
FROM_ADDRESS=
EXCEPTIONS_LOG_FILE= 
````
If these above variables are in a projects .env file, they will be used when sending notifications. For one off emails with the
`Notifications.email()` method, the `to_address` and `from_address` can be overwritten. The `EXCEPTIONS_LOG_FILE` is necessary if you want a specific path to create this file. If this variable is not set, an `exceptions.log` file will be created at the project's root.

## Getting Started
The entry point to the notifications package is through the `create_notificaiotns` function. This returns a notifications object. The function requires two arguments: 
1) the name you want to give the job and 
2) which mail service you want to use (there are currently two services, “mailgun” and  “gmail”).  

There is a third optional argument where you can pass the location of a log file to be attached to the notification message.
 
```
from job_notifications import create_notifications

notifications = create_notifications('Some Project', "mailgun", logs='/path/to/some/log.file')
```
Typically with ELT jobs at KIPP Nor Cal, we use the notifications in a try/except block under the `if __name__ == "__main__":` block:
```
if __name__ == '__main__':
    try:
        main()
        notifications.notify()
    except Exception as e:
        notifications.notify(error_message="Uh-oh!")
```
Importing the built-in traceback module can give better error messages than "Uh-oh!":
```
if __name__ == '__main__':
    try:
        main()
        notifications.notify()
    except Exception as e:
        stack_trace = traceback.format_exc()
        notifications.notify(error_message=stack_trace)
```
## Extras
Here are some extra features that are nice to have.
### Error Handling
If there is a common error occurring that you would like to capture without crashing the ETL job, the function where the error occurs can be decorated with a `@handled_exception` decorator.
This decorator will take the exception you expect to catch as an argument or a tuple of exceptions if you are catching more than one.

```
from job_notifications import handled_exception

@handled_exception(ValueError)
def multiples_of_three(x):
    if x % 3 != 0:
        raise ValueError("Not a multiple of three!")
    else:
        logging.info(f"{x} is a multiple of three!")
```
If any exceptions are caught, the Slack message will have "Succeeded with Warnings" as the subject line, and the message will have a log attached listing all of teh exceptions caught and where.
### Timer
Want to log how fast a function is?
```
from job_notifications import timer

@timer()
def do_nothing():
    logging.info("I'm doing nothing")
    sleep(20)
```
It's a fairly basic decorator that will log the names of the module, the function and the time it took for the function to finish. Sometimes the names of the modules and functions can be unpleasant to read. These can be replaced by passing a string:
```
@timer("This function does nothing")
def do_nothing():
    logging.info("I'm doing nothing")
    sleep(20)
```

### Argument Logging

## Future Plans