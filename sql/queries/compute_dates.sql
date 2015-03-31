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
      SET   computed_date_start = CASE
                                    WHEN sub.prev_date IS NULL THEN
                                      CASE
                                        WHEN d.interpolation = 'start' THEN
                                          --               [C---
                                          d.date
                                        ELSE
                                          --             ---C---
                                          NULL
                                      END
                                    ELSE
                                      CASE 
                                        WHEN sub.prev_interpolation = 'start' THEN
                                          CASE
                                            WHEN d.interpolation = 'start' THEN
                                              --    [P--------][C---
                                              d.date
                                            WHEN d.interpolation = 'end' THEN
                                              --    [P----][----C]
                                              (sub.prev_date+d.date)/2.0
                                            ELSE -- WHEN d.interpolation = 'default' THEN
                                              --    [P----][----C---
                                              (sub.prev_date+d.date)/2.0

                                          END
                                        WHEN sub.prev_interpolation = 'end' THEN
                                          CASE
                                            WHEN d.interpolation = 'start' THEN
                                              --    ---P]        [C---
                                              -- this is a contradiction, so we take the center
                                              (sub.prev_date+d.date)/2.0
                                            WHEN d.interpolation = 'end' THEN
                                              --    ---P][--------C]
                                              sub.prev_date
                                            ELSE -- WHEN d.interpolation = 'default' THEN
                                              --    ---P][--------C---
                                              sub.prev_date
                                          END
                                        ELSE -- WHEN sub.prev_interpolation = 'default' THEN
                                          CASE
                                            WHEN d.interpolation = 'start' THEN
                                              --    ---P--------][C---
                                              d.date
                                            WHEN d.interpolation = 'end' THEN
                                              --    ---P----][----C]
                                              (sub.prev_date+d.date)/2.0
                                            ELSE -- WHEN d.interpolation = 'default' THEN
                                              --    ---P----][----C---
                                              (sub.prev_date+d.date)/2.0
                                          END
                                      END
                                  END,
            computed_date_end =   CASE
                                    WHEN sub.next_date IS NULL THEN
                                      CASE
                                        WHEN d.interpolation = 'end' THEN
                                          --             ---C]
                                          d.date
                                        ELSE
                                          --             ---C---
                                          NULL
                                      END
                                    ELSE
                                      CASE 
                                        WHEN d.interpolation = 'start' THEN
                                          CASE
                                            WHEN sub.next_interpolation = 'start' THEN
                                              --    [C--------][N---
                                              sub.next_date
                                            WHEN sub.next_interpolation = 'end' THEN
                                              --    [C----][----N]
                                              (sub.next_date+d.date)/2.0
                                            ELSE -- WHEN sub.next_interpolation = 'default' THEN
                                              --    [C----][----N---
                                              (sub.next_date+d.date)/2.0

                                          END
                                        WHEN d.interpolation = 'end' THEN
                                          CASE
                                            WHEN sub.next_interpolation = 'start' THEN
                                              --    ---C]        [N---
                                              -- this is a contradiction, so we take the center
                                              (sub.next_date+d.date)/2.0
                                            WHEN sub.next_interpolation = 'end' THEN
                                              --    ---C][--------N]
                                              d.date
                                            ELSE -- WHEN sub.next_interpolation = 'default' THEN
                                              --    ---C][--------N---
                                              d.date
                                          END
                                        ELSE -- WHEN d.interpolation = 'default' THEN
                                          CASE
                                            WHEN sub.next_interpolation = 'start' THEN
                                              --    ---C--------][N---
                                              sub.next_date
                                            WHEN sub.next_interpolation = 'end' THEN
                                              --    ---C----][----N]
                                              (sub.next_date+d.date)/2.0
                                            ELSE -- WHEN sub.next_interpolation = 'default' THEN
                                              --    ---C----][----N---
                                              (sub.next_date+d.date)/2.0
                                          END
                                      END
                                  END
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
            entity_id IN (SELECT b_id FROM vtm.related_entities WHERE a_id=%(entity_id)s)    -- a related entity's properties have been edited
          )
          AND
          (property_type_id = %(property_type_id)s)
		GROUP BY date, property_type_id
		ORDER BY date ASC
	) as sub
	WHERE 	d.id = ANY(sub.ids);