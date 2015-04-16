/*******************************/
/* SOURCES                     */
/*******************************/

INSERT INTO vtm.sources(name)
SELECT 'UN_VOL'
WHERE NOT EXISTS ( SELECT id FROM vtm.sources WHERE name = 'UN_VOL' );


/*******************************/
/* ENTITY_TYPES                */
/*******************************/

INSERT INTO vtm.entity_types(name,min_zoom,max_zoom,zindex)
SELECT 'building', 15, null, 3.0
WHERE NOT EXISTS ( SELECT id FROM vtm.entity_types WHERE name = 'building' );


/*******************************/
/* ENTITIES                    */
/*******************************/

INSERT INTO vtm.entities (name, type_id)
SELECT 	'un_vol_entity_'||source.id_0 as name,
		(SELECT id FROM vtm.entity_types WHERE name='building') as type_id
FROM 	"data_external"."un_vol" as source
WHERE 	ST_Intersects(source.geom, ST_MakeEnvelope(2311190,5034958,2311882,5035316,3004) );


/*******************************/
/* EVENTS (geom)               */
/*******************************/

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	ent.id as entity_id,
		0 as property_type_id,
		ST_Transform(source.geom,4326) as geovalue,
		2015 as date,
		(SELECT id FROM vtm.sources WHERE name='UN_VOL') as source_id
FROM 	"data_external"."un_vol" as source
LEFT JOIN 	vtm.entities as ent ON ent.name=('un_vol_entity_'||source.id_0)
WHERE 	ST_Intersects(source.geom, ST_MakeEnvelope(2311190,5034958,2311882,5035316,3004));




/*******************************/
/* EVENTS (height              */
/*******************************/

INSERT INTO vtm.properties_types(name) VALUES ('height');

INSERT INTO vtm.properties(entity_id, property_type_id, value, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('un_vol_entity_'||source.id_0) LIMIT 1) as entity_id,
		(SELECT id FROM vtm.properties_types WHERE name='height') as property_type_id,
		uv_qcolmo as value,
		2015 as date,
		(SELECT id FROM vtm.sources WHERE name='UN_VOL') as source_id
FROM 	"data_external"."un_vol" as source
WHERE 	ST_Intersects(source.geom, ST_MakeEnvelope(2311190,5034958,2311882,5035316,3004));