/************************************************************************************************/
/* GEOMETRY_BY_BORDERS GET ENTITIES TO POSTPROCESS
 *
 * Given a list of modified entities (potential borders), this query returns all entities whose geometry must be recomputed
 *
 *
 * params:
 *    modified_entities_ids  :      the modified entities
 */
/************************************************************************************************/

SELECT 	DISTINCT entity_id
FROM	vtm.properties
WHERE	property_type_id=2 AND value::integer = ANY(%(modified_entities_ids)s);