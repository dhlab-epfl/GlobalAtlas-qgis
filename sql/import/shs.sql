/************************************************************************************************/
/* IMPROT SHS
 *
 * This query imports data from the shs table
 *
 *
 */
/************************************************************************************************/


SELECT 	vtm.insert_properties_helper(t.entity_name, 'border', 'source_description', 'geom', substring(t.date,0,5)::int, 'start', ST_AsText(t.geom))
FROM	data_external.shs_base_data as t;

