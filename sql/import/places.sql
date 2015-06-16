
SELECT 	vtm.insert_properties_helper('Place '||name, 'place'::text, null, 'geom'::text, null, null, ST_AsText(geom))
FROM   "data_external"."places";

SELECT 	vtm.insert_properties_helper('Place '||name, 'place'::text, null, 'name'::text, null, null, name)
FROM   "data_external"."places";