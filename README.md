# Talos

<a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg"></a> [![talos-deploy](https://github.com/npitsillos/talos/actions/workflows/talos-deploy.yml/badge.svg)](https://github.com/npitsillos/talos/actions/workflows/talos-deploy.yml) [![talos-release](https://github.com/npitsillos/talos/actions/workflows/talos-package.yml/badge.svg)](https://github.com/npitsillos/talos/actions/workflows/talos-package.yml)[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/npitsillos/talos/main.svg)](https://results.pre-commit.ci/latest/github/npitsillos/talos/main)


# Overview
Talos assists members of a discord server in creating, submitting, and in general interface with the Kaggle API in order to compete to Kaggle competitions. It also allows for people to attempt tutorials in fields such as data science, deep learning and AI through google colab notebooks.

# Installation
## Using Pip
Talos can be installed either via pip:

`pip install talosbot`

This installs Talos in your current Python environment and exposes Talos' `talosbot` cli.  This requires a running MongoDB server which you can run in a docker container like so:

`docker run -d -p 27017-27019:27017-27019 --name mongodb mongo`

You now need to run the command `talosbot setupenv` to create a `.env` file.

Finally, to launch the bot simply run `talosbot run`.

## Using Docker
> This is the recommended approach for when you want to contribute to Talos.

This method runs the MongoDB server out of the box and uses `docker-compose` to build an image and run it in a container.

Initially run the following command to clone the repository:

`git clone https://github.com/npitsillos/talos.git && cd talos`

Now run this after setting up your `.env` file:

### Production

`docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`

### Development
`docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`

## Contributors
* [npitsillos](https://github.com/npitsillos)

### Please feel free to contribute