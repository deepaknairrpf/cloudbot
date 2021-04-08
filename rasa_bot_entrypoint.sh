#!/bin/bash
rasa run --model rasa_bot/models/cloud_bot_model.tar.gz --endpoints rasa_bot/endpoints.yml &
exec "$@"