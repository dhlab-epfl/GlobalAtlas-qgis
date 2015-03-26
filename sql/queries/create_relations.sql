/************************************************************************************************/
/* CREATE RELATIONS
 *
 * This query creates relations between all provided entities
 * 
 * Features should be postprocessed afterwards.
 *
 *
 * params:
 *    entities_ids  :      the array entities to relate
 */
/************************************************************************************************/

INSERT INTO vtm.related_entities(
	a_id,
	b_id
)
SELECT *
FROM unnest(%(entities_ids)s) as t
JOIN  unnest(%(entities_ids)s) as u ON t<>u;