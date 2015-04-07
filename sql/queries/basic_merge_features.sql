/************************************************************************************************/
/* MERGE FEATURES
 *
 * This query sets the entity_id for a set of properties
 * 
 * Features should be postprocessed afterwards.
 *
 *
 * params:
 *    entity_id  :      the id of the entity to postprocess
 *    property_ids  :   a set of properties ids
 */
/************************************************************************************************/

UPDATE vtm.properties as d
      SET   entity_id = %(entity_id)s
      WHERE id = ANY( %(property_ids)s );