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
