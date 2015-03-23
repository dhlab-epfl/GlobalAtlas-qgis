# TimeMachineGlobal Plugin

This plugin is intended to edit the database of the Time Machine Global database.

It ships a QGIS project which must be used to use the plugin.

<!-- MarkdownTOC depth=3 -->

- Getting started
- Reference
    - Slider
    - Help button
    - ID button
    - Open button
    - Data
    - Shape
    - Entity
    - Sucession
    - View

<!-- /MarkdownTOC -->

---------

## Getting started

Click on the "open" button to load the QGIS project.

You're now seeing the TimeMachineGlobal map. You can browse through time using the slider of the main dock window.

---------

## Reference

### Slider

You can slide the slider to choose which date to choose. You can set the min/max of the slider values using the two boxes on each side of the slider.


### Help button

Shows this help.


### ID button

(Will be removed) Show the id of the selected layer in the console. For developement purposes.


### Open button

Loads the provided QGIS file. You must start with this file to work with the plugin, because it makes use of the file's layer IDs. This means you can save your file as another name if you want to add your own layers.


### Data

#### Load

This opens the load data dialog, which is used to import data from other layers in the TMG database.


### Shape

#### Copy at date

Creates a copy of the selected shape at the current slider date. The shape must be in one of the properties tables.

#### Doest not exist at date

Sets the geometry property of the selcted shape to NULL for the current date. The shape must be in one of the properties tables.


### Entity

#### Merge

Use this to merge two different properties so that they refer to the same entity.

#### Explode

This will create new entities so that all selected properties refer to a different entity.


### Sucession

#### Create

Use this to set a relation of sucession between two different entities.

#### Remove

Use this to remove a relation of sucession between two different entities.



### View

#### See properties

This will show the properties table and select all properties related to the selected entity. This is useful to review all properties of an entity. Best used with QGIS' option "show selected attribute".

#### See entity

This will show the entity table and select the selected entity. This is useful to change the name or type of an entity. Best used with QGIS' option "show selected attribute".

#### See relations

This will show the relations table and select all relations of the selected entity. Best used with QGIS' option "show selected attribute".
