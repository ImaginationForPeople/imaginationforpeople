#!/bin/bash

#where manage.py is
PROJECT_DIR="TO_COMPLETE"

cd $PROJECT_DIR

source ../bin/activate

./manage.py send_email_alerts

deactivate
