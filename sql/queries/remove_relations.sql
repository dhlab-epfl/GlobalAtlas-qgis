/************************************************************************************************/
/* REMOVE RELATIONS
 *
 * This query removes relations between all provided entities
 * 
 * Features should be postprocessed afterwards.
 *
 *
 * params:
 *    entities_ids  :      the array entities to relate
 */
/************************************************************************************************/

DELETE FROM vtm.related_entities
WHERE a_id = ANY( %(entities_ids)s ) OR b_id = ANY( %(entities_ids)s );