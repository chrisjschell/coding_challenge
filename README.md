## Install:

You can use a virtual environment (conda, venv, etc):
```
conda env create -f environment.yml
source activate user-profiles
```

Or just pip install from the requirements file
``` 
pip install -r requirements.txt
```

## Running the code

### Spin up the service

```
# start up local server
python -m run 
```

### Making Requests

```
curl -i "http://127.0.0.1:5000/health-check"
```

```
curl -i "http://127.0.0.1:5000/aggregate?bitbucket=ORG&github=ORG"
```

## Running the tests

```
python -m unittest discover
```


## What'd I'd like to improve on...
First and foremost I would like to improve my test coverage. I covered all functionality from a happy path perspective and the connection errors one is likely to run in to, however not every edge case is covered. Additionally, on that note I would like to research the APIs more thoroughly to understand any possible error situations one is likely to run into while using them and make sure my API is capable of handling them. That being said the error handling is robust and designed to return "default" or "zeroed" values if data cannot be found. Due to that approach I would also spend more time on logging to ensure that silent errors can be researched and rectified if need be, but from a user perspective this approach makes for a seamless and dependable experience. Error handling for the Flask API itself could be more robust but I did not spend time on it.

I would also like to pin a version number on the 'requests' entry in the requirements file, however due to the fact that I am running Python 3.8 and the current versions in the requirements file are non-functioning versions for 3.8 I decided to leave 'requests' unpinned in the hopes that it would default to a valid requests version.

Certainly if this system went into production, Github's rate limiting would need to be accounted for. Currently zero results are returned from Github in the event of hitting the rate limit. At a minimum there should be loging to account for the rate limit, and possibly a note in the response body if there is no other means to get around the limiting.

Finally, there might be more efficient means to acquiring the data within the APIs themselves. I was thorough in my research but I simply did not have sufficient time to be an absolute expert on either API.
