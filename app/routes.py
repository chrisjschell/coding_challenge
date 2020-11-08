"""API routes file to collect data from both Bitbucket and Github APIs"""

# Standard Library
import logging

# Third Party
import flask
from flask import jsonify, request, Response

# Project Library
from app.services.bitbucket import Bitbucket
from app.services.github import Github
from app.tools.combine import combine

app = flask.Flask("user_profiles_api")
logger = flask.logging.create_logger(app)
logger.setLevel(logging.INFO)


@app.route("/health-check", methods=["GET"])
def health_check():
  """
  Endpoint to health check API
  """
  app.logger.info("Health Check!")
  return Response("All Good!", status=200)


@app.route("/aggregate", methods=["GET"])
def aggregate():
  """
  Aggregate information from both Bitbucket and Github APIs

  Query Params:
      bitbucket (str): Name of bitbucket organization
      github (str): Name of github organization

  Returns:
      dict|str: Aggregated results if both query parameters are provided or an error
      string indicating one or more query parameters were not successfully provided
  """
  app.logger.info("GET - Aggregator")
  args = request.args

  if not args.get('bitbucket') or not args.get('github'):
    return Response('Missing query string parameters "bitbucket" and/or "github"')

  app.logger.info("Bitbucket organization provided: %s", args.get('bitbucket'))
  app.logger.info("Github organization provided: %s", args.get('github'))

  bitbucket = Bitbucket(args.get('bitbucket'))
  github = Github(args.get('github'))

  bitbucket_results = bitbucket.make_response()
  github_results = github.make_response()

  results = combine(bitbucket_results, github_results)

  return jsonify(results)
