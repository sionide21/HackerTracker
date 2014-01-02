Installation
============

The easiest way to get up and running is with [Heroku](https://devcenter.heroku.com/articles/quickstart).


## Step 1: Create the app

    heroku create

## Step 2: Add a database

Add a Heroku database instance to your app. We expect the `DATABASE_URL` environment variable to be used so you have to "promote" the database Heroku provides.

    heroku addons:add heroku-postgresql
    heroku pg:promote $(heroku config | grep HEROKU_POSTGRESQL | cut -f 1 -d :)

## Step 3: Secure the tracker

Create an auth token that will be required to track events. Here we just generate a random one. If you skip this step, anyone can post events.

    heroku config:set AUTH_TOKEN="$(head /dev/random | md5)"

You will need this token later. If you forget it, you can recover it with `heroku config:get AUTH_TOKEN`

## Step 4: Deploy the code

    git push heroku master

## Step 5: Configure the database

    heroku run src/configure_database.py

That's it, you can now visit your tracker with `heroku open`