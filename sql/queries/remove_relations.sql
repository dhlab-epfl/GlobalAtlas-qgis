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

DELETE FROM vtm.properties
WHERE 		property_type_id=3
			AND
			( 
				entity_id = ANY( %(entities_ids)s ) 
				OR
				value::integer = ANY( %(entities_ids)s ) 
			);