### Simple authorization microservice
#### This service requires flask and requests, beside that it utilizes python builtins. 

#### Usage
##### Docker
1. Clone this repo and enter it
2. Create docker image utilizing docker's buildx `docker buildx build . -t accessverifier --load`
3. Create container out of image `docker run --rm -p "8080:8080/tcp" accessverifier`
4. Verify by using curl `curl -XPOST localhost:8080/authroize -H "X-Forwarded-For: 18.153.184.148" -H "Content-type: text/plain"` 
##### Virtual env
1. Clone this repo and enter it
2. Create virtualenv `python -m venv ven`
3. Activate virtualenv `source venv/bin/activate` 
4. Install requirements `pip install -r requirements.txt`
5. Run app from terminal `python main.py`
6. Verify by using curl `curl -XPOST localhost:8080/authroize -H "X-Forwarded-For: 18.153.184.148" -H "Content-type: text/plain"` 
