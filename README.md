# VeniceTimeMachine Plugin

This plugin is a very lite version of the time manager plugin. It allows to filter vector layers with an integer date, not limited to post 1900 dates.

To use, simply filter your vector layers with a filter containing a string like `/**/1824/**/`.

The plugin will change the date to whatever is entered by the user using the slider or the text box.

A typical use would be setting the following filter for one layer :

    "start_year"<=/**/1601/**/ AND "end_year">=/**/1601/**/