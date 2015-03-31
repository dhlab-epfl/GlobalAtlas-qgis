/************************************************************************************************/
/* INSTALL view_for_qgis
 *
 * This creates a view to be used in QGIS.
 *
 * REQUIRES geom_extension
 */
/************************************************************************************************/

/*************************************************/
/* View                                          */
/*************************************************/

DROP VIEW IF EXISTS vtm.properties_for_qgis CASCADE;

CREATE VIEW vtm.properties_for_qgis AS
SELECT 	ev.id,
		ev.description,
		ev.property_type_id,
		ev.value,
		ev.geovalue,
		ev.date,
		ev.interpolation,
		ev.entity_id,
		ev.source_id,
		ev.source_description,
		ev.computed_date_start,
		ev.computed_date_end,
		ent.name as entity_name,
		type.name as entity_type_name,
		prop.name as property_name
FROM vtm.properties as ev
JOIN vtm.properties_types as prop ON ev.property_type_id=prop.id
JOIN vtm.entities as ent ON ev.entity_id=ent.id
JOIN vtm.entity_types as type ON ent.type_id=type.id;
ALTER VIEW vtm.properties_for_qgis ALTER COLUMN id SET DEFAULT nextval('vtm.properties_id_seq'::regclass); -- we need this so that QGIS knows it must autoincrement the id on creation


/*************************************************/
/* Trigger to make it updatable                  */
/*************************************************/

DROP FUNCTION IF EXISTS vtm.proxy_properties_for_qgis() CASCADE;
CREATE FUNCTION vtm.proxy_properties_for_qgis() RETURNS trigger AS    
$$
    BEGIN

      IF TG_OP='INSERT' THEN

      	IF NEW.property_type_id IS NULL THEN
      		NEW.property_type_id = 1; -- if no property_type_id is provided, we probably want a geo property
      	END IF;

      	INSERT INTO vtm.properties( id, description, property_type_id, value, geovalue, date, interpolation, entity_id, source_id, source_description	)
      	VALUES ( NEW.id, NEW.description, NEW.property_type_id, NEW.value, NEW.geovalue, NEW.date, NEW.interpolation, NEW.entity_id, NEW.source_id, NEW.source_description);
	    RETURN NEW;


      ELSIF TG_OP='UPDATE' THEN

      	IF NEW.property_type_id IS NULL THEN
      		NEW.property_type_id = 1; -- if no property_type_id is provided, we probably want a geo property
      	END IF;

      	UPDATE vtm.properties SET
	      	id=NEW.id,
	      	description=NEW.description,
	      	property_type_id=NEW.property_type_id,
	      	value=NEW.value,
	      	geovalue=NEW.geovalue,
	      	date=NEW.date,
	      	interpolation=NEW.interpolation,
	      	entity_id=NEW.entity_id,
	      	source_id=NEW.source_id,
	      	source_description=NEW.source_description
	    WHERE id=OLD.id;
		RETURN NEW;


      ELSIF TG_OP='DELETE' THEN

		DELETE FROM vtm.properties WHERE id=OLD.id;
		RETURN OLD;


      END IF;


    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER proxy_properties_for_qgis INSTEAD OF INSERT OR UPDATE OR DELETE ON vtm.properties_for_qgis FOR EACH ROW
    EXECUTE PROCEDURE vtm.proxy_properties_for_qgis();