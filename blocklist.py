"""
blocklist.py

This file contains the blocklist of the JWT tokens. It will be imported by
app and the logout resource so that tokens can be added to the blocklist when the
user logs out.


Important stuff:

It is likely that you would want to use a database(Redis) other than a Python set to
store the blocklist. This is because the set will be reset every time the
application is restarted. This means that users will be logged out when the
application is restarted.

Say a Redis database to store the blocklist. Redis is an in-memory data structure
store, used as a database, cache and message broker.

In short: Python set's don't persist inbetween app restarts. So when ever you
save the file after changes, we have Flask in Debug Mode so that restarts the app,
the Blocklist gets deleted, therefore the previous jwt's now work until there
expire date
"""

BLOCKLIST = set()