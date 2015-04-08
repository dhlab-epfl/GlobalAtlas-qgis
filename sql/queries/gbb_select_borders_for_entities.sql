/************************************************************************************************/
/* GEOMETRY_BY_BORDERS SELECT BORDERS FOR ENTITIES
 *
 * Select all corresponding borders properties for entities
 *
 *
 * params:
 *    entities_ids  :      the entities
 */
/************************************************************************************************/

SELECT 	id
FROM 	vtm.properties
WHERE   entity_id::text IN (

			SELECT 	value
			FROM 	vtm.properties
			WHERE 	property_type_id=2
					AND
					entity_id = ANY( %(entities_ids)s )

		);