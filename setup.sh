#!/bin/bash
export DATABASE_URL="postgresql://postgres:abc@localhost:5432/planetary_planner"
export DATABASE_NAME="planetary_planner"
export AUTH0_CLIENT_ID="86dZTvlBGDJ4MEoo5TdWVkmOnyAbLTQG"
export AUTH0_CLIENT_SECRET="A8asHmHN9bT-4bBuI_tVPllb-QQ9wNWV6BjzHpS0aK-z_Pi14Ccm2TNW0JufbF3C"
export AUTH0_DOMAIN="pla.us.auth0.com"
export API_AUDIENCE="planetaryplanner/api"
export APP_SECRET_KEY="a9c8b69d7cbf43987790b74f38393b24193348e360c23462a12ad8ea53ad6be3"
export LOGLEVEL="DEBUG"
export PORT="3000"
echo "setup.sh script executed successfully!"