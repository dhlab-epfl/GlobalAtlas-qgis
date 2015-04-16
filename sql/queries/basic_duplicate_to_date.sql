/************************************************************************************************/
/* DUPLICATE TO DATE
 *
 * This query sets copies a set of properties to a certain date
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
		value,
		%(date)s
FROM vtm.properties
WHERE id = ANY (%(property_ids)s);