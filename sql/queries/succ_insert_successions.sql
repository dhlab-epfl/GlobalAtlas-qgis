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

INSERT INTO 	vtm.properties(entity_id, property_type_id, value)
SELECT 			t as entity_id,
				3 as property_type_id,
				u::text as value
FROM 			unnest(%(entities_ids)s) as t
JOIN  			unnest(%(entities_ids)s) as u ON t<>u;
