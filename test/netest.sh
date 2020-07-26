#!/bin/bash

cd umbralPre
source venv/bin/activate
cd server
nohup flask run -h 0.0.0.0 -p 5022 > /dev/null 2>&1 &
