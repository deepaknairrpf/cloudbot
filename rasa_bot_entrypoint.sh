#!/bin/bash
#rasa run  --port 5005 --connector slack --credentials rasa_bot/credentials.yml --model rasa_bot/models/cloud_bot_model.tar.gz --endpoints rasa_bot/endpoints.yml --cors * --enable-api --debug &
rasa run --port 5005 --credentials rasa_bot/credentials.yml --model rasa_bot/models/cloud_bot_model.tar.gz --endpoints rasa_bot/endpoints.yml --debug &
exec "$@"