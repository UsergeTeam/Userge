FROM gitpod/workspace-full

# Simply install Heroku CLI
# Just in case we use Gitpod for deployment.
RUN curl https://cli-assets.heroku.com/install.sh | -