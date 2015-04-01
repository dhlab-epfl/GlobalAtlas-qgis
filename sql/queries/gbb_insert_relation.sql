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

INSERT INTO vtm.geom_by_borders(entity_id, border_id)
SELECT  %(entity_id)s as entity_id,
		unnest( %(borders_ids)s ) as border_id;