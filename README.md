# TimeMachineGlobal Plugin

This plugin is intended to edit the database of the Time Machine Global database.

It ships a QGIS project which must be used to use the plugin.

<!-- MarkdownTOC depth=3 -->

- Getting started
- Principles
- More details
- Reference - The Toolbar
    - Slider
    - Help button !Load data icon
    - ID button
    - Open button
    - Import data !Load data icon
    - Copy at date
    - Doest not exist at date
    - Merge entities
    - Explode entities
    - Create Sucession
    - Remove Sucession
    - View properties
    - View entity
- Reference - The Load data dialog

<!-- /MarkdownTOC -->

---------

## Getting started

Click on the "open" button to load the QGIS project.

You're now seeing the TimeMachineGlobal map. You can browse through time using the slider of the main dock window.

---------

## Principles

Every object appearing in TimeMachineGlobal is an *entity*. An *entity* is nothing more than an absolute reference of an object such as a building, a person, a city, etc.

The *entity* has *properties*. A *property* is nothing more than a certain value for a certain aspect of an entity at a given date.

Using the dates of properties, we are able to display an entity at any given date by interpolating (TODO : explain ?) between properties.

Example :

Let's say we have an entitiy called Entity_1 representing the City of Istanbul.

We could have the following properties to model the name of the city :

| entity   | property  | date  | value          |
| ---------|-----------|-------|----------------|
| Entity_1 | name      | -630  | Byzantium      |
| Entity_1 | name      | 330   | Constantinople |
| Entity_1 | name      | 1930  | Istanbul       |


We could have the following properties to model the population :

| entity   | property   | date | value      |
| ---------|-----------|-------|------------|
| Entity_1 | population | 1550 | 700'000    |
| Entity_1 | population | 1950 | 1'000'000  |
| Entity_1 | population | 2014 | 14'377'019 |

The geometry appearing on the map is working exactly the same way :

| entity   | property | date | value             |
| ---------|----------|------|-------------------|
| Entity_1 | geom     | 1950 | [POLYGON(...)][1] |
| Entity_1 | geom     | 2014 | [POLYGON(...)][1] |

[1]: http://en.wikipedia.org/wiki/Well-known_text  "Description of WKT format"

## More details

TODO : explain computed_date_start/computed_date_end and interpolation



---------

## Reference - The Toolbar

### Slider

You can slide the slider to choose which date to choose. You can set the min/max of the slider values using the two boxes on each side of the slider.

### Help button ![Load data icon](images/icon_help.png) 

Shows this help.

### ID button

(Will be removed) Show the id of the selected layer in the console. For developement purposes.

### Open button

Loads the provided QGIS file. You must start with this file to work with the plugin, because it makes use of the file's layer IDs. This means you can save your file as another name if you want to add your own layers.

### Import data ![Load data icon](images/icon_import.png) 

This opens the [load data dialog](#load_data_dialog), which is used to import data from other layers in the TMG database.

### Copy at date

Creates a copy of the selected shape at the current slider date. The shape must be in one of the properties tables.

### Doest not exist at date

Sets the geometry property of the selcted shape to NULL for the current date. The shape must be in one of the properties tables.

### Merge entities

Use this to merge two different properties so that they refer to the same entity.

### Explode entities

This will create new entities so that all selected properties refer to a different entity.


### Create Sucession

Use this to set a relation of sucession between two different entities.

### Remove Sucession

Use this to remove a relation of sucession between two different entities.

### View properties

This will show the properties table and select all properties related to the selected entity. This is useful to review all properties of an entity. Best used with QGIS' option "show selected attribute".

### View entity

This will show the entity table and select the selected entity. This is useful to change the name or type of an entity. Best used with QGIS' option "show selected attribute".



## Reference - The Load data dialog

This dialog allows to load data from a QGIS layer.

Example :

We're loading a shapefile of buildings that have the field ANNEE_CONS that holds the building year (or 0 if unknown) and the field HAUTEUR that holds the height of the building.

By default, the loading window is configured to import the geometry property only, at current date, and with default interpolation.
In this case, here's how we could load the height property.

![Load dialog screenshot](images/help_load_screenshot.png) 

*Property* 

This simply holds the name of the property.

```
height
```


*Date*

This expression sets the date to 2015 if no building date is known. The same expression is used for all properties.

```
CASE
    WHEN "ANNEE_CONS"=0 THEN 2015
    ELSE "ANNEE_CONS"
END 
```


*Interpolation*

This expression sets the interpolation to 'default' if no building date is known (meaning that the date is lying somewhere in the existence of the building, but we don't know where), or to 'start' if a building date is known (meaning that the date corresponds the the start of the property's validity).  The same expression is used for all properties.

```
CASE
    WHEN "ANNEE_CONS"=0 THEN 'default'
    ELSE 'start'
END 
```


*Value*

This expression is preentered for geometrical layers, and will convert the geometry to it's WKT representation in the EPSG:4326 system.

```
geomToWKT( transform($geometry,'EPSG:4326','EPSG:4326') )
```

