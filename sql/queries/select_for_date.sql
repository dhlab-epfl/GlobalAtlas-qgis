/************************************************************************************************/
/* SELECT FOR DATE
 *
 * This query selects all geometries that must be displayed at a certain date
 * 
 * params:
 *    date  :   			 the date
 */
/************************************************************************************************/

SELECT 	prop.id,
		prop.entity_id,
		prop.date,
		ST_AsGeoJSON(
			ST_Simplify(
				geovalue,
				360.0/pow(2.0,:zoom+9.0)
			)
		) as geojson
FROM vtm.properties as prop
WHERE 	(computed_date_start IS NULL OR computed_date_start<=&(date)s) -- we only want properties that have started
		AND
		(computed_date_end IS NULL OR computed_date_end>&(date)s) -- we only want properties that have not ended