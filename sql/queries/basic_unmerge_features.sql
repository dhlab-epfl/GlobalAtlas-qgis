/************************************************************************************************/
/* UNMERGE FEATURES
 *
 * This query sets the entity_id to null for a set of properties
 * 
 * This will result in the creation of a new entity for each of those property.
 *
 *
 * params:
 *    property_ids  :   a set of properties ids
 */
/************************************************************************************************/

UPDATE vtm.properties as d
      SET   entity_id = NULL
      WHERE id = ANY( %(property_ids)s )
RETURNING entity_id, property_type_id;