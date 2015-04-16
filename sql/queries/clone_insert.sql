/************************************************************************************************/
/* CLONE INSERT
 *
 * Inserts a copy property, that will dynamically clone the key/value from another property to a different date/interpolation
 *
 *
 * params:
 *    properties_ids  :    the id of the property we're copying
 *    date  :    				the date
 */
/************************************************************************************************/

INSERT INTO vtm.properties(entity_id, property_type_id, value, date)
SELECT  entity_id as entity_id,
		4 as property_type_id,
		id as value,
		%(date)s as date
FROM    vtm.properties
WHERE 	id = ANY( %(properties_ids)s );