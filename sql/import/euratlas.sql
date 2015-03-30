/************************************************************************************************/
/* IMPROT EURATLAS
 *
 * This query imports data from the euratlas table
 *
 *
 * params:
 *    from_date  :      the date from which to start
 *    to_date  :      the date to which to go
 */
/************************************************************************************************/

SELECT 	vtm.insert_properties_helper(t.long_name, 'sovereign_state'::text, 'Euratlas', 'geom'::text, t.year::int, 'start', ST_AsText(ST_Transform(geom,4326)))
FROM	"data_external"."euratlas_sovereign_states" as t
WHERE year>=%(from_date)s AND year<=%(to_date)s;

SELECT 	vtm.insert_properties_helper(t.long_name, 'sovereign_state'::text, 'Euratlas', 'geom'::text, t.year::int+100, 'start', NULL)
FROM	"data_external"."euratlas_sovereign_states" as t
WHERE year>=%(from_date)s AND year<=%(to_date)s;




/*******************************/
/* RELATIONS                   */
/*******************************/

/* ALGORITHM 3 : set succession relation for entities that overlap */
/*
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