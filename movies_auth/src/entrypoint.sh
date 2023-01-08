#!/usr/bin/env bash
flask --app app/flask_app.py db upgrade || exit 2
python main.py