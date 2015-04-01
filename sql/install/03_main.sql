/************************************************************************************************/
/* INSTALL main
 *
 * This installs the main tables
 */
/************************************************************************************************/

/*************************************************/
/* Table properties_types                        */
/*************************************************/

DROP TABLE IF EXISTS vtm.properties_types CASCADE;
CREATE TABLE vtm.properties_types
(
  id serial NOT NULL PRIMARY KEY,
  name text UNIQUE,
  description text,
  type text,
  subtype text,
  creation_timestamp timestamp default now(),
  creation_user text default CURRENT_USER,
  modification_timestamp timestamp default now(),
  modification_user text default CURRENT_USER
);

CREATE TRIGGER properties_types_stamps BEFORE INSERT OR UPDATE ON vtm.properties_types FOR EACH ROW
    EXECUTE PROCEDURE vtm.stamp();

/*************************************************/
/* Table entity_types                            */
/*************************************************/

DROP TABLE IF EXISTS vtm.entity_types CASCADE;
CREATE TABLE vtm.entity_types
(
  id serial NOT NULL PRIMARY KEY,
  name text UNIQUE,
  min_zoom int,
  max_zoom int,
  zindex real,
  creation_timestamp timestamp default now(),
  creation_user text default CURRENT_USER,
  modification_timestamp timestamp default now(),
  modification_user text default CURRENT_USER
);

CREATE TRIGGER entity_types_stamps BEFORE INSERT OR UPDATE ON vtm.entity_types FOR EACH ROW
    EXECUTE PROCEDURE vtm.stamp();

/*************************************************/
/* Table entities                                */
/*************************************************/

DROP TABLE IF EXISTS vtm.entities CASCADE;
CREATE TABLE vtm.entities
(
  id serial NOT NULL PRIMARY KEY,
  name text,
  type_id integer NOT NULL DEFAULT 1 REFERENCES vtm.entity_types ON DELETE CASCADE,
  creation_timestamp timestamp default now(),
  creation_user text default CURRENT_USER,
  modification_timestamp timestamp default now(),
  modification_user text default CURRENT_USER
);
COMMENT ON TABLE vtm.entities IS 'Cette table contient les entités historiques.';

CREATE TRIGGER entities_stamps BEFORE INSERT OR UPDATE ON vtm.entities FOR EACH ROW
    EXECUTE PROCEDURE vtm.stamp();



/*************************************************/
/* Table related_entities                        */
/*************************************************/

DROP TABLE IF EXISTS vtm.related_entities CASCADE;
CREATE TABLE vtm.related_entities
(
  id serial NOT NULL PRIMARY KEY,
  a_id integer NOT NULL REFERENCES vtm.entities ON DELETE CASCADE,
  b_id integer NOT NULL REFERENCES vtm.entities ON DELETE CASCADE,
  creation_timestamp timestamp default now(),
  creation_user text default CURRENT_USER,
  modification_timestamp timestamp default now(),
  modification_user text default CURRENT_USER
);
COMMENT ON TABLE vtm.related_entities IS 'Cette table contient les entités liées par une relation de succession.';

-- TRIGGER FOR STAMPS

CREATE TRIGGER related_entities_stamps BEFORE INSERT OR UPDATE ON vtm.related_entities FOR EACH ROW
    EXECUTE PROCEDURE vtm.stamp();






/*************************************************/
/* Table sources                                 */
/*************************************************/

DROP TABLE IF EXISTS vtm.sources CASCADE;
CREATE TABLE vtm.sources
(
  id serial NOT NULL PRIMARY KEY,
  name text UNIQUE,
  creation_timestamp timestamp default now(),
  creation_user text default CURRENT_USER,
  modification_timestamp timestamp default now(),
  modification_user text default CURRENT_USER
);
COMMENT ON TABLE vtm.sources IS 'Cette table contient les documents sources.';

-- TRIGGER FOR STAMPS

CREATE TRIGGER sources_stamps BEFORE INSERT OR UPDATE ON vtm.sources FOR EACH ROW
    EXECUTE PROCEDURE vtm.stamp();


/*************************************************/
/* Table properties                              */
/*************************************************/

-- TABLE

DROP TABLE IF EXISTS vtm.properties CASCADE;
CREATE TABLE vtm.properties
(
  id serial NOT NULL PRIMARY KEY,
  entity_id integer NOT NULL REFERENCES vtm.entities ON DELETE CASCADE,
  description text,
  property_type_id integer NOT NULL REFERENCES vtm.properties_types ON DELETE CASCADE,
  value text,
  date integer,
  interpolation vtm.interpolation_type NOT NULL DEFAULT 'default',
  computed_date_start integer,
  computed_date_end integer,
  --computed_size real,
  source_id integer REFERENCES vtm.sources ON DELETE SET NULL,
  source_description text,
  creation_timestamp timestamp default now(),
  creation_user text default CURRENT_USER,
  modification_timestamp timestamp default now(),
  modification_user text default CURRENT_USER
);
DROP FUNCTION IF EXISTS vtm.properties_stamps() CASCADE;

-- TRIGGER FOR STAMPS

CREATE TRIGGER properties_trigger_A_stamps BEFORE INSERT OR UPDATE ON vtm.properties FOR EACH ROW
    EXECUTE PROCEDURE vtm.stamp();


-- TRIGGER TO CREATE AN ENTITY IF NONE IS PROVIDED

DROP FUNCTION IF EXISTS vtm.autogenerate_entity() CASCADE;

CREATE FUNCTION vtm.autogenerate_entity() RETURNS trigger AS    
$$
    DECLARE
        new_entity_id integer;
    BEGIN
        IF NEW.entity_id IS NULL THEN
          INSERT INTO "vtm"."entities"("name","type_id") VALUES ('entity_'||lpad(currval('vtm.entities_id_seq')::text,6,'0'), 1);
          NEW.entity_id = ( SELECT currval('vtm.entities_id_seq') );
        END IF;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER properties_trigger_B_autogenerate BEFORE INSERT OR UPDATE OF entity_id ON vtm.properties FOR EACH ROW
    EXECUTE PROCEDURE vtm.autogenerate_entity();


-- TRIGGER SET INTERPOLATION TO DEFAULT

DROP FUNCTION IF EXISTS vtm.autoset_interpolation() CASCADE;

CREATE FUNCTION vtm.autoset_interpolation() RETURNS trigger AS    
$$
    DECLARE
        new_entity_id integer;
    BEGIN
        IF NEW.interpolation IS NULL THEN
          NEW.interpolation = 'default';
        END IF;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER properties_trigger_B_autoset_interpolation BEFORE INSERT OR UPDATE OF interpolation ON vtm.properties FOR EACH ROW
    EXECUTE PROCEDURE vtm.autoset_interpolation();



-- TRIGGER TO RECOMPUTE DATES WHEN PROPERTIES ARE ADDED

/*
CREATE TRIGGER reset_date_for_properties AFTER INSERT OR UPDATE OF "date","property_type_id","entity_id" OR DELETE ON vtm.properties FOR EACH ROW
    EXECUTE PROCEDURE vtm.properties_reset_computed_dates();
*/

