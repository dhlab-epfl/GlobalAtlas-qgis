/************************************************************************************************/
/* INSTALL geom_extension
 *
 * This extends the properties set to manage geovalues.
 *
 * REQUIRES geom_extension
 */
/************************************************************************************************/

/*************************************************/
/* Add the geovalue column and the spatial index */
/*************************************************/

ALTER TABLE vtm.properties ADD COLUMN geovalue geometry(Geometry,4326);
CREATE INDEX properties_geovalue_gix ON vtm.properties USING GIST (geovalue);

/*************************************************/
/* Add the triggers                              */
/*************************************************/

DROP FUNCTION IF EXISTS vtm.properties_geovalue_manager() CASCADE;
CREATE FUNCTION vtm.properties_geovalue_manager() RETURNS trigger AS    
$$
    BEGIN

		IF TG_OP='INSERT' THEN
		  	IF NEW.property_type_id=1 THEN -- if we insert a "geom" property
			  	IF NEW.geovalue IS NOT NULL THEN
			      	NEW.value = ST_AsText(NEW.geovalue); -- we set the value acording to geovalue, if a geovalue was provided
			    ELSE
			    	NEW.geovalue = ST_GeomFromText(NEW.value, 4326); -- we set the geovalue acording to value, if no geovalue was provided
			    END IF;
		    END IF;
		    RETURN NEW;

		ELSIF TG_OP='UPDATE' THEN
		  	IF NEW.property_type_id=1 THEN -- if we update a "geom" property
			  	IF NOT ST_Equals(NEW.geovalue, OLD.geovalue) THEN -- we set the value acording to geovalue, if the geovalue was changed
			      	NEW.value = ST_AsText(NEW.geovalue);
			    ELSE
			    	NEW.geovalue = ST_GeomFromText(NEW.value, 4326); -- we set the geovalue acording to value, if the geovalue was not changed
			    END IF;
			ELSIF OLD.property_type_id=1 AND NEW.property_type_id<>1 THEN
		    	NEW.geovalue = NULL; -- we unset the geovalue if we are no more in a "geom" property
		    END IF;
		    RETURN NEW;

		ELSE
		    RETURN NULL;   

	  END IF;


    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER properties_trigger_C_geovalue BEFORE INSERT OR UPDATE OF "property_type_id","geovalue","value" ON vtm.properties FOR EACH ROW
    EXECUTE PROCEDURE vtm.properties_geovalue_manager();
