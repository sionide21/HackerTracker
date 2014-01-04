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

This step is optional but highly recommended unless you are running in a private network.

### Restrict tracking access

Create an auth token that will be required to track events. Here we just generate a random one. If you skip this step, anyone can post events.

    heroku config:set AUTH_TOKEN="$(head /dev/random | md5)"

You will need this token later. If you forget it, you can recover it with `heroku config:get AUTH_TOKEN`

### Restrict front end access

You can restrict web access to a specific openid identity. Even if you don't know it, you probably [already have an openid identity](http://stackoverflow.com/questions/1116743/where-can-i-find-a-list-of-openid-provider-urls).

You will need Memcached for session storage

    heroku addons:add memcachedcloud

Now set your open id identity url:

    OPENID_AUTH_IDENTITY=https://profiles.google.com/<your id>


## Step 4: Deploy the code

    git push heroku master

## Step 5: Configure the database

    heroku run src/configure_database.py

That's it, you can now visit your tracker with `heroku open`