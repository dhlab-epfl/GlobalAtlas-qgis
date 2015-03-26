/************************************************************************************************/
/* SELECT ENTITY AND PROPERTY TYPE
 *
 * This query returns the entity_id and the property_type_id of a property.
 * It can be useful to get those value before deleting a property, to be able
 * to run postprocessing afterwards.
 * 
 * Features should be postprocessed afterwards.
 *
 *
 * params:
 *    pid  :      the property id
 *
 * returns: (should be 1 result)
 * 	  entity_id, property_type_id
 */
/************************************************************************************************/

SELECT entity_id, property_type_id FROM vtm.properties WHERE id=%(pid)s