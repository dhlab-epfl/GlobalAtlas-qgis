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
/* Function to calculate date from two dates and interpolations */
/*************************************************/

DROP FUNCTION IF EXISTS vtm.compute_interpolation(dateA integer, inA vtm.interpolation_type, dateB integer, inB vtm.interpolation_type) CASCADE;
CREATE FUNCTION vtm.compute_interpolation(dateA integer, inA vtm.interpolation_type, dateB integer, inB vtm.interpolation_type) RETURNS integer AS    
$$
    BEGIN
        IF dateA IS NULL AND dateB IS NULL THEN                 /*    ∞----------∞  */
            RETURN NULL;
        ELSIF dateA IS NULL THEN
            IF inB = 'start' THEN                               /*    ∞         [B    */
                RETURN dateB;
            ELSE                                                /*    ∞----------B    */
                RETURN NULL;
            END IF;
        ELSIF dateB IS NULL THEN
            IF inA = 'end' THEN                                 /*    A]         ∞    */
                RETURN dateA;
            ELSE                                                /*    A----------∞    */
                RETURN NULL;
            END IF;
        ELSE
            IF inA = 'end' THEN
                IF inB = 'start' THEN                           /*    A]   ?!   [B    */  -- this is a contradiction, so we take the center
                    RETURN round((dateA+dateB)/2.0)::integer;
                ELSE                                            /*    A][--------B    */
                    RETURN dateA;
                END IF;
              ELSE
                IF inB = 'start' THEN                           /*    A--------][B    */
                    RETURN dateB;
                ELSE                                            /*    A----][----B    */
                    RETURN round((dateA+dateB)/2.0)::integer;
                END IF;
            END IF;
        END IF;
    END;
$$ LANGUAGE plpgsql;

/*************************************************/
/* Function to recompute a date for a property of an entity */
/*************************************************/

DROP FUNCTION IF EXISTS vtm.compute_date_for_property_of_entity(the_entity_id integer, the_property_id integer) CASCADE;
CREATE FUNCTION vtm.compute_date_for_property_of_entity(the_entity_id integer, the_property_id integer) RETURNS VOID AS    
$$
    BEGIN
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
                  entity_id = the_entity_id                                                        -- the entity's properties have been edited
                  OR
                  entity_id::text IN  (
                        SELECT  succ.value
                        FROM  vtm.properties as succ
                        WHERE   succ.property_type_id=3 AND succ.entity_id = the_entity_id
                      )
                )
                AND
                (property_type_id = the_property_id)
          GROUP BY date, interpolation, property_type_id
          ORDER BY date, interpolation ASC
        ) as sub
        WHERE   d.id = ANY(sub.ids);
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


/*************************************************/
/* Functions to facilitate inserts               */
/*************************************************/

DROP FUNCTION IF EXISTS vtm.insert_properties_helper(entity_name text, entity_type_name text, source_name text, property_name text, dat integer, interp vtm.interpolation_type, val text) CASCADE;
CREATE FUNCTION vtm.insert_properties_helper(entity_name text, entity_type_name text, source_name text, property_name text, dat integer, interp vtm.interpolation_type, val text) RETURNS integer AS    
$$
    DECLARE
      ent_type_id integer;
      ent_id integer;
      prp_type_id integer;
      src_id integer;
      return_id integer;
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
      INSERT INTO vtm.properties( entity_id, property_type_id, source_id, date, interpolation, value  ) VALUES ( ent_id, prp_type_id, src_id, dat, interp, val ) RETURNING id INTO return_id;

      RETURN return_id;

    END;
$$ LANGUAGE plpgsql;

