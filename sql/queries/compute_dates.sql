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

UPDATE vtm.properties as d
      SET   computed_date_start = vtm.compute_interpolation(sub.prev_date,sub.prev_interpolation,d.date,d.interpolation),
            computed_date_end = vtm.compute_interpolation(d.date,d.interpolation,sub.next_date,sub.next_interpolation)
	FROM (
		SELECT  array_agg(id) as ids,
		      date,
		      lag(date, 1, NULL) OVER (ORDER BY date) as prev_date,
		      lead(date, 1, NULL) OVER (ORDER BY date) as next_date,                  
		      MIN(interpolation) as interpolation,
		      lag(MIN(interpolation), 1, NULL) OVER (ORDER BY date) as prev_interpolation,
		      lead(MIN(interpolation), 1, NULL) OVER (ORDER BY date) as next_interpolation
		FROM vtm.properties
		WHERE (
            entity_id = %(entity_id)s                                                        -- the entity's properties have been edited
            OR
            entity_id::text IN 	(
									SELECT 	succ.value
									FROM 	vtm.properties as succ
									WHERE 	succ.property_type_id=3 AND succ.entity_id = %(entity_id)s
								)
          )
          AND
          (property_type_id = %(property_type_id)s)
		GROUP BY date, property_type_id
		ORDER BY date ASC
	) as sub
	WHERE 	d.id = ANY(sub.ids);