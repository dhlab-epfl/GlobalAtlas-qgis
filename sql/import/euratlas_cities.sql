/************************************************************************************************/
/* IMPROT EURATLAS
 *
 * This query imports data from the euratlas table
 *
 *
 * params:
 *    year  :      the date to import
 */
/************************************************************************************************/

-- remove useless or duplicate data
/*
DELETE FROM data_external.euratlas_cities
WHERE id_0 NOT IN (
		SELECT DISTINCT ON (id, year, size, name) id_0
		FROM data_external.euratlas_cities
		ORDER BY year
	)*/

SELECT 	vtm.insert_properties_helper('City #'||t.id, 'city'::text, 'Euratlas', 'geom'::text, t.year::int, 'start', ST_AsText(ST_Transform(t.geom,4326))),
		vtm.insert_properties_helper('City #'||t.id, 'city'::text, 'Euratlas', 'size'::text, t.year::int, 'start', size::text),
		vtm.insert_properties_helper('City #'||t.id, 'city'::text, 'Euratlas', 'name'::text, t.year::int, 'start', name::text)
FROM	data_external.euratlas_cities as t
WHERE 	year=%(year)s;






/*******************************/
/* RELATIONS                   */
/*******************************/

/* ALGORITHM 3 : set succession relation for entities that overlap */
/*
OBSOLETE !! vtm.related_entities has been replaced by succession_relation type
INSERT INTO vtm.related_entities(a_id, b_id)
SELECT 	evA.entity_id as a_id,
		evB.entity_id as b_id
FROM 	vtm.properties as evA
JOIN 	vtm.properties as evB 		ON 		ST_Intersects(evA.geovalue, evB.geovalue)
JOIN 	vtm.entities as entA	ON 		evA.entity_id = entA.id
JOIN 	vtm.entities as entB	ON 		evB.entity_id = entB.id
WHERE   (evA.date = evB.date+100 OR evA.date = evB.date-100)
		AND
	 	evA.source_id = ( SELECT id FROM vtm.sources WHERE name = 'Euratlas' )
	 	AND
	 	evB.source_id = ( SELECT id FROM vtm.sources WHERE name = 'Euratlas' );
*/