/*******************************/
/* SOURCES                     */
/*******************************/

INSERT INTO vtm.sources(name)
SELECT 'Isabella di Lenardo'
WHERE NOT EXISTS ( SELECT id FROM vtm.sources WHERE name = 'Isabella di Lenardo' );


/*******************************/
/* ENTITY_TYPES                */
/*******************************/

INSERT INTO vtm.entity_types(name,min_zoom,max_zoom,zindex)
SELECT 'isola', 10, null, 2.0
WHERE NOT EXISTS ( SELECT id FROM vtm.entity_types WHERE name = 'isola' );

INSERT INTO vtm.entity_types(name,min_zoom,max_zoom,zindex)
SELECT 'building', 15, null, 3.0
WHERE NOT EXISTS ( SELECT id FROM vtm.entity_types WHERE name = 'building' );

INSERT INTO vtm.entity_types(name,min_zoom,max_zoom,zindex)
SELECT 'canal', 10, null, 1.0
WHERE NOT EXISTS ( SELECT id FROM vtm.entity_types WHERE name = 'canal' );


/*******************************/
/* ENTITIES                    */
/*******************************/

INSERT INTO vtm.entities (name, type_id)
SELECT 	'1360_isl_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='isola') as type_id
FROM 	"data_draft_idl"."1360_isl" as source;

INSERT INTO vtm.entities (name, type_id)
SELECT 	'xiisec_isl_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='isola') as type_id
FROM 	"data_draft_idl"."xiisec_isl" as source;

INSERT INTO vtm.entities (name, type_id)
SELECT 	'1360_can_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='canal') as type_id
FROM 	"data_draft_idl"."1360_can" as source;

INSERT INTO vtm.entities (name, type_id)
SELECT 	'xiisec_can_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='canal') as type_id
FROM 	"data_draft_idl"."xiisec_can" as source;

INSERT INTO vtm.entities (name, type_id)
SELECT 	'1808_un_vol copy_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='building') as type_id
FROM 	"data_draft_idl"."1808_un_vol copy" as source;

INSERT INTO vtm.entities (name, type_id)
SELECT 	'1360_un_vol copy_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='building') as type_id
FROM 	"data_draft_idl"."1360_un_vol copy" as source;

INSERT INTO vtm.entities (name, type_id)
SELECT 	'13th_un_vol copy_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='building') as type_id
FROM 	"data_draft_idl"."13th_un_vol copy" as source;

INSERT INTO vtm.entities (name, type_id)
SELECT 	'xiisec_un_vol copy_entity_'||id as name,
		(SELECT id FROM vtm.entity_types WHERE name='building') as type_id
FROM 	"data_draft_idl"."xiisec_un_vol copy" as source;


/*******************************/
/* EVENTS (geom)               */
/*******************************/

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('1360_isl_entity_'||source.id) LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_CollectionExtract(ST_MakeValid(ST_Transform(source.geom,4326)),3) as geovalue,
		1360 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_draft_idl"."1360_isl" as source;

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('xiisec_isl_entity_'||source.id) LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_CollectionExtract(ST_MakeValid(ST_Transform(source.geom,4326)),3) as geovalue,
		1150 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_draft_idl"."xiisec_isl" as source;

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('1360_can_entity_'||source.id) LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_CollectionExtract(ST_MakeValid(ST_Transform(source.geom,4326)),3) as geovalue,
		1360 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_draft_idl"."1360_can" as source;

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('xiisec_can_entity_'||source.id) LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_CollectionExtract(ST_MakeValid(ST_Transform(source.geom,4326)),3) as geovalue,
		1150 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_draft_idl"."xiisec_can" as source;

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('1808_un_vol copy_entity_'||source.id) LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_CollectionExtract(ST_MakeValid(ST_Transform(source.geom,4326)),3) as geovalue,
		1808 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_draft_idl"."1808_un_vol copy" as source;

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('1360_un_vol copy_entity_'||source.id) LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_CollectionExtract(ST_MakeValid(ST_Transform(source.geom,4326)),3) as geovalue,
		1360 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_draft_idl"."1360_un_vol copy" as source;

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('13th_un_vol copy_entity_'||source.id) LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_CollectionExtract(ST_MakeValid(ST_Transform(source.geom,4326)),3) as geovalue,
		1250 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_draft_idl"."13th_un_vol copy" as source;

INSERT INTO vtm.properties(entity_id, property_type_id, geovalue, date, source_id)
SELECT 	(SELECT id FROM vtm.entities WHERE name=('xiisec_un_vol copy_entity_'||source.id) LIMIT 1) as entity_id,
		0 as property_type_id,
		ST_CollectionExtract(ST_MakeValid(ST_Transform(source.geom,4326)),3) as geovalue,
		1150 as date,
		(SELECT id FROM vtm.sources WHERE name='Isabella di Lenardo') as source_id
FROM 	"data_draft_idl"."xiisec_un_vol copy" as source;





/*******************************/
/* RELATIONS                   */
/*******************************/

/* ALGORITHM 1 : merge when there is no change at all */

UPDATE vtm.properties as e1
SET entity_id = e2.entity_id
FROM vtm.properties as e2
WHERE 	e1.property_type_id=0
		AND
		e2.property_type_id=0
		AND
		e1.id<e2.id
		AND
		ST_Equals(e1.geovalue,e2.geovalue)
		AND
	 	e1.source_id = ( SELECT id FROM vtm.sources WHERE name = 'Isabella di Lenardo' )
		AND
	 	e2.source_id = ( SELECT id FROM vtm.sources WHERE name = 'Isabella di Lenardo' );


/* ALGORITHM 2 : merge when there is only a small change */

UPDATE vtm.properties as e1
SET entity_id = e2.entity_id
FROM vtm.properties as e2
WHERE 	e1.property_type_id = 0
		AND 	
	 	e2.property_type_id = 0
		AND
		e1.id<e2.id
		AND
		ST_IsValid(e1.geovalue)
		AND
		ST_IsValid(e2.geovalue)
		AND
		ST_Intersects(e1.geovalue, e2.geovalue)
		AND
		ST_Area( ST_Intersection(e1.geovalue,e2.geovalue) ) > 0.95*GREATEST(ST_Area( e1.geovalue),ST_Area( e2.geovalue))
		AND
	 	e1.source_id = ( SELECT id FROM vtm.sources WHERE name = 'Isabella di Lenardo' )
		AND
	 	e2.source_id = ( SELECT id FROM vtm.sources WHERE name = 'Isabella di Lenardo' );