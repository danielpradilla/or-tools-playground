# or-tools-playground
having fun with Google or-tools

https://github.com/google/or-tools

https://developers.google.com/optimization/



Create the docker container from within the docker directory
docker build -t danielpradilla/or-tools .

And then run it from the root of the application
docker run --rm -v www:/app/www --name or-tools-gunicorn -p 5000:80 danielpradilla/or-tools

(change 5000 for the port that you wish to use)
