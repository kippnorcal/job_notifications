# job_notifications
![Tests](https://github.com/kippnorcal/job_notifications/actions/workflows/tests.yml/badge.svg)

A simple package for sending notifications to Slack.

## Dependencies


## Installation


## Set Up
The repo currently supports two ways to send emails: 1) via MailGun API or 2) via Google SMTP email. Whichever method used needs to be declared when instantiating the package (see "Getting Started" below). Both methods require credentials. Credentials can be passed at time of instantiation or stored in a .env file. For security reasons, storing credentials in a .env file is teh recommended method.

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


## Future Plans