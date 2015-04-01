/************************************************************************************************/
/* INSTALL functions
 *
 * This installs functions and types used by the system
 */
/************************************************************************************************/

/*************************************************/
/* TYPE interpolation_type                      */
/*************************************************/

DROP TYPE IF EXISTS vtm.interpolation_type CASCADE;
CREATE TYPE vtm.interpolation_type AS ENUM ('start','default','end');


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


/*************************************************/
/* Functions to facilitate inserts               */
/*************************************************/

DROP FUNCTION IF EXISTS vtm.insert_properties_helper(entity_name text, entity_type_name text, source_name text, property_name text, dat integer, interp vtm.interpolation_type, val text) CASCADE;
CREATE FUNCTION vtm.insert_properties_helper(entity_name text, entity_type_name text, source_name text, property_name text, dat integer, interp vtm.interpolation_type, val text) RETURNS VOID AS    
$$
    DECLARE
      ent_type_id integer;
      ent_id integer;
      prp_type_id integer;
      src_id integer;
    BEGIN
    
      -- CREATE THE ENTITY TYPE IF IT DOESNT EXIST
      ent_type_id := (SELECT id FROM vtm.entity_types WHERE name=entity_type_name);

      IF ent_type_id IS NULL THEN
        INSERT INTO vtm.entity_types(name) VALUES(entity_type_name) RETURNING id INTO ent_type_id;
      END IF;

    
      -- CREATE THE ENTITY IF IT DOESNT EXIST
      ent_id := (SELECT id FROM vtm.entities WHERE name=entity_name);

      IF ent_id IS NULL THEN
        INSERT INTO vtm.entities(name, type_id) VALUES(entity_name, ent_type_id) RETURNING id INTO ent_id;
      END IF;

    
      -- CREATE THE PROPERTY TYPE IF IT DOESNT EXIST
      prp_type_id := (SELECT id FROM vtm.properties_types WHERE name=property_name);

      IF prp_type_id IS NULL THEN
        INSERT INTO vtm.properties_types(name) VALUES(property_name) RETURNING id INTO prp_type_id;
      END IF;

    
      -- CREATE THE SOURCE IF IT DOESNT EXIST
      src_id := (SELECT id FROM vtm.sources WHERE name=source_name);

      IF src_id IS NULL THEN
        INSERT INTO vtm.sources(name) VALUES(source_name) RETURNING id INTO src_id;
      END IF;


      -- FINALLY INSERT THE PROPERTY
      INSERT INTO vtm.properties( entity_id, property_type_id, source_id, date, interpolation, value  ) VALUES ( ent_id, prp_type_id, src_id, dat, interp, val );


    END;
$$ LANGUAGE plpgsql;



/*************************************************/
/* Functions to recompute dates                  */ -- THIS IS NOT USED CURRENTLY
/*************************************************/
/*
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
*/
-- TRIGGER TO RECOMPUTE DATES
-- should be put after the relations table
/*
DROP FUNCTION IF EXISTS vtm.relations_reset_computed_dates();
CREATE FUNCTION vtm.relations_reset_computed_dates() RETURNS trigger AS    
$$
    BEGIN

      IF TG_OP='INSERT' OR TG_OP='UPDATE' THEN
        PERFORM vtm.query_reset_computed_dates(NEW.a_id, NULL);
      END IF;
      
      IF TG_OP='UPDATE' OR TG_OP='DELETE' THEN
        PERFORM vtm.query_reset_computed_dates(OLD.a_id, NULL);
      END IF;       

      IF TG_OP='UPDATE' OR TG_OP='INSERT' THEN
        RETURN NEW;
      ELSE
        RETURN OLD;
      END IF;

    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER reset_date_for_relations AFTER INSERT OR UPDATE OF "a_id","b_id" OR DELETE ON vtm.related_entities FOR EACH ROW
    EXECUTE PROCEDURE vtm.relations_reset_computed_dates();
*/