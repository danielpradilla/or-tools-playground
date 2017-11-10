based on https://github.com/texastribune/docks/tree/master/gunicorn

Creates a gunicorn insance with nginx reverse proxy on port 80

The container is expecting you to mount a volume at /app/www with the neccessary files, including an or-tools_api.py file

Run from outside the directory as
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml run


or 

From within the directory
docker build --no-cache -t danielpradilla/or-tools .

and then from the root of the application
docker run -v `pwd`/www:/app/www -p 5000:80 -d --name or-tools-gunicorn  danielpradilla/or-tools 

(change 5000 for the port that you wish to use)
