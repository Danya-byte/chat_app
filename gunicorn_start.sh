#!/bin/bash
NAME="your_app_name"
VENV_PATH="/path/to/your/project/venv/bin/activate"
APP_PATH="/path/to/your/project"
SOCKFILE="$APP_PATH/gunicorn.sock"
NUM_WORKERS=3
LOG_LEVEL=debug

source $VENV_PATH
cd $APP_PATH

exec gunicorn ${NAME}:app \
  --bind=unix:$SOCKFILE \
  --workers $NUM_WORKERS \
  --log-level=$LOG_LEVEL \
  --log-file=-