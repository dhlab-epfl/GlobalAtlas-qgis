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

SELECT 	vtm.insert_properties_helper(t.long_name, 'state'::text, 'Euratlas', 'geom'::text, t.year::int, 'start', ST_AsText(ST_Transform(geom,4326)))
FROM	"data_external"."euratlas_sovereign_states" as t
WHERE year=%(year)s;

SELECT 	vtm.insert_properties_helper(t.long_name, 'state'::text, 'Euratlas', 'geom'::text, t.year::int+100, 'start', NULL)
FROM	"data_external"."euratlas_sovereign_states" as t
WHERE year=%(year)s;




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