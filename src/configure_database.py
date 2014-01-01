#! /usr/bin/env python
import os
from sqlalchemy import create_engine
from hackertracker.database import Model

from hackertracker import event  # Load the models
assert event  # silence pyflakes


def main():
    dburl = os.environ['DATABASE_URL']
    print "Setting up database '%s'..." % dburl
    engine = create_engine(dburl, echo=True)
    engine.connect()
    Model.metadata.create_all(engine)
    print "Done"


if __name__ == '__main__':
    main()
