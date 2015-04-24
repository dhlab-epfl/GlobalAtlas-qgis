/************************************************************************************************/
/* COMPUTE DATES
 *
 * This query computes the computed_date_start and computed_date_end for
 * all properties of a given type for a given entity and for it's relation.
 *
 *
 * params:
 *    entity_id  :      the id of the entity to postprocess
 *    property_type_id  : the type of property to postprocess
 */
/************************************************************************************************/

SELECT vtm.compute_date_for_property_of_entity(sub.entity_id,sub.property_type_id)
FROM (
	SELECT DISTINCT entity_id, property_type_id FROM vtm.properties
) as sub;
