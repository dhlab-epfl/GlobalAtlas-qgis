
/*************************************************/
/* Functions to recompute dates                  */
/*************************************************/

-- GENERIC TRIGGER FUNCTION

DROP FUNCTION IF EXISTS vtm.properties_reset_computed_dates();
CREATE FUNCTION vtm.properties_reset_computed_dates() RETURNS trigger AS    
$$
    BEGIN
      IF TG_OP='INSERT' OR TG_OP='UPDATE' THEN
        PERFORM vtm.query_reset_computed_dates(NEW.entity_id, NEW.property_type_id);
      END IF;
      
      IF TG_OP='UPDATE' OR TG_OP='DELETE' THEN
        PERFORM vtm.query_reset_computed_dates(OLD.entity_id, OLD.property_type_id);
      END IF;       

      IF TG_OP='UPDATE' OR TG_OP='INSERT' THEN
        RETURN NEW;
      ELSE
        RETURN NULL;
      END IF;
    END;
$$ LANGUAGE plpgsql;

-- ACTUAL FUNCTION CALLED

DROP FUNCTION IF EXISTS vtm.query_reset_computed_dates(current_entity_id int, current_property_type_id integer);
CREATE FUNCTION vtm.query_reset_computed_dates(current_entity_id int, current_property_type_id integer) RETURNS VOID AS
$$
    BEGIN
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
          WHERE (entity_id=current_entity_id OR entity_id IN (SELECT b_id FROM vtm.related_entities WHERE a_id=current_entity_id)) AND (current_property_type_id IS NULL OR property_type_id=current_property_type_id)
          GROUP BY date, property_type_id
          ORDER BY date ASC
        ) as sub
        WHERE entity_id=current_entity_id AND (current_property_type_id IS NULL OR property_type_id=current_property_type_id) AND d.id = ANY(sub.ids);
    END;
$$ LANGUAGE plpgsql;


/*************************************************/
/* Functions to store date and user stamps       */
/*************************************************/


DROP FUNCTION IF EXISTS vtm.stamp() CASCADE;
CREATE FUNCTION vtm.stamp() RETURNS trigger AS    
$$
    BEGIN
      IF TG_OP='INSERT' THEN
        NEW.creation_timestamp = NOW();
        NEW.creation_user = CURRENT_USER;
        RETURN NEW;
      ELSIF TG_OP='UPDATE' THEN
        NEW.modification_timestamp = NOW();
        NEW.modification_user = CURRENT_USER;
        RETURN NEW;
      ELSE
        RETURN NULL;      
      END IF;
    END;
$$ LANGUAGE plpgsql;