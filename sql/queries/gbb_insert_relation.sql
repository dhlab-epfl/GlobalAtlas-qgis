/************************************************************************************************/
/* GEOMETRY_BY_BORDERS INSERT RELATION
 *
 * Insert borders for an entity
 *
 *
 * params:
 *    entity_id  :      the entity
 *    borders_ids  :    array of border entities
 */
/************************************************************************************************/

INSERT INTO vtm.properties(entity_id, property_type_id, value)
SELECT  %(entity_id)s as entity_id,
		2 as property_type_id,
		unnest( %(borders_ids)s ) as value;