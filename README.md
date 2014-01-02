Hacker Tracker
==============

A scriptable way to track arbitrary aspects of your life.

Make a request to `/track/<eventname>` and it will be recorded for later analysis.

## Usage

The most basic usage is to simply log an occurrence of an event. The following will add an occurrence of "Drink glass of water" right now:

```sh
curl http://tracker.example.com/track/Drink%20glass%20of%20water
```

Underscores are converted to spaces so the above request can be written as

```sh
curl http://tracker.example.com/track/Drink_glass_of_water
```

You can associate arbitrary attributes with events by posting them:

```sh
curl -d "size=16" -d "location=office" http://tracker.example.com/track/Drink_glass_of_water
```

### Security

If you want to restrict access to the tracker, set the environment variable `AUTH_TOKEN` to a secret. This token will be required to track any event.

for example: if the key is `secr3t`, start the server with:

    AUTH_TOKEN="secr3t" python src/app.py

To log events, use:

```sh
curl -d "size=16" -d "location=office" -H "X-Auth-Token: secr3t" http://tracker.example.com/track/Drink_glass_of_water
# or
curl -d "size=16" -d "location=office" http://tracker.example.com/track/Drink_glass_of_water?auth=secr3t
```