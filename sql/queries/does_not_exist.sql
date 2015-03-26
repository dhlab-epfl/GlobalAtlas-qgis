/************************************************************************************************/
/* DOES NOT EXIST
 *
 * This query sets the entity_id for a set of properties
 * 
 * Features should be postprocessed afterwards.
 *
 *
 * params:
 *    properties_ids  :      all the property to set to NULL
 *    date  :   			 the date
 */
/************************************************************************************************/

INSERT INTO vtm.properties(
	entity_id,
	property_type_id,
	value,
	date
)
SELECT 	entity_id,
		property_type_id,
		NULL,
		%(date)s
FROM vtm.properties
WHERE id = ANY( %(property_ids)s );