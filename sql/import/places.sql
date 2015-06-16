
SELECT 	vtm.insert_properties_helper('Place '||name, 'place'::text, 'None', 'geom'::text, null, null, ST_AsText(geom))
FROM   "data_external"."places";

SELECT 	vtm.insert_properties_helper('Place '||name, 'place'::text, 'None', 'name'::text, null, null, name)
FROM   "data_external"."places";