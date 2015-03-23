/*******************************/
/* SOURCES                     */
/*******************************/

INSERT INTO vtm.sources(name)
SELECT 'Euratlas'
WHERE NOT EXISTS ( SELECT id FROM vtm.sources WHERE name = 'Euratlas' );


/*******************************/
/* ENTITY_TYPES                */
/*******************************/

INSERT INTO vtm.entity_types(name,min_zoom,max_zoom,zindex)
SELECT 'sovereign_state', null, 12, 50.0
WHERE NOT EXISTS ( SELECT id FROM vtm.entity_types WHERE name = 'sovereign_state' );


/*******************************/
/* ENTITIES                    */
/*******************************/

INSERT INTO vtm.entities (name, type_id)
SELECT 	long_name as name,
		(SELECT id FROM vtm.entity_types WHERE name='sovereign_state') as type_id
FROM 	"data_external"."euratlas_sovereign_states"
/*WHERE year>=1500*/;


/*******************************/
/* EVENTS (geom)               */
/*******************************/

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=source.long_name LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_Transform(source.geom,4326) as geovalue,
		year::int as date,
		(SELECT id FROM vtm.sources WHERE name='Euratlas') as source_id
FROM 	"data_external"."euratlas_sovereign_states" as source
/*WHERE year>=1500*/;



/*******************************/
/* RELATIONS                   */
/*******************************/

/* ALGORITHM 3 : set succession relation for entities that overlap */
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