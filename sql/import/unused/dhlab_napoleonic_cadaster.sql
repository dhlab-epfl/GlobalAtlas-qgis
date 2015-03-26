/*******************************/
/* SOURCES                     */
/*******************************/

INSERT INTO vtm.sources(name)
SELECT 'Napoleonic Cadaster'
WHERE NOT EXISTS ( SELECT id FROM vtm.sources WHERE name = 'Napoleonic Cadaster' );

INSERT INTO vtm.sources(name)
SELECT 'Isabella di Lenardo'
WHERE NOT EXISTS ( SELECT id FROM vtm.sources WHERE name = 'Isabella di Lenardo' );


/*******************************/
/* ENTITY_TYPES                */
/*******************************/

INSERT INTO vtm.entity_types(name,min_zoom,max_zoom,zindex)
SELECT 'lot', 19, null, 5.0
WHERE NOT EXISTS ( SELECT id FROM vtm.entity_types WHERE name = 'lot' );


/*******************************/
/* ENTITIES                    */
/*******************************/

INSERT INTO vtm.entities (name, type_id)
SELECT 	'napoleonic_lot_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='lot') as type_id
FROM 	"data_vectorized_historical_cadasters"."nap12" as source
WHERE 	ST_Intersects(ST_Transform(source.geom,4326), ST_MakeEnvelope(12.3328,45.4365,12.3401,45.4401, 4326));


/*******************************/
/* EVENTS (geom)               */
/*******************************/

INSERT INTO vtm.events(entity_id, key, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('napoleonic_lot_entity_'||source.id) LIMIT 1) as entity_id,
		'geom' as key,
		ST_Transform(source.geom,4326) as geovalue,
		1808 as date,
		(SELECT id FROM vtm.sources WHERE name='Napoleonic Cadaster') as source_id
FROM 	"data_vectorized_historical_cadasters"."nap12" as source
WHERE 	ST_Intersects(ST_Transform(source.geom,4326), ST_MakeEnvelope(12.3328,45.4365,12.3401,45.4401, 4326));



/*******************************/
/* EVENTS (code)               */
/*******************************/

INSERT INTO vtm.events(entity_id, key, value, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('napoleonic_lot_entity_'||source.id) LIMIT 1) as entity_id,
		'code' as key,
		cod as value,
		1808 as date,
		(SELECT id FROM vtm.sources WHERE name='Napoleonic Cadaster') as source_id
FROM 	"data_vectorized_historical_cadasters"."nap12" as source
WHERE 	ST_Intersects(ST_Transform(source.geom,4326), ST_MakeEnvelope(12.3328,45.4365,12.3401,45.4401, 4326));



/*******************************/
/* EVENTS (owner)              */
/*******************************/

INSERT INTO vtm.events(entity_id, key, value, date, source_id)
SELECT 	ev.entity_id as entity_id,
		'owner' as key,
		"PROPR" as value,
		1808 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_vectorized_historical_cadasters"."Nap_SM" as source
JOIN 	vtm.events as ev ON key='code' AND value="source"."Num";