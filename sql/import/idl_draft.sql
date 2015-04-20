/*******************************/
/* DATA                        */
/*******************************/

/* ISOLA */

SELECT 	vtm.insert_properties_helper('Isola 1360 '||id, 'isola'::text, 'Isabella draft', 'clone'::text, 1808, 'end'::vtm.interpolation_type, pid::text)
FROM   (
	SELECT 	vtm.insert_properties_helper('Isola 1360 '||id, 'isola'::text, 'Isabella draft', 'geom'::text, 1360, 'start'::vtm.interpolation_type, ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Transform(geom,4326)),3))) as pid,
			id as id
	FROM	"data_draft_idl"."1360_isl" as t
	) as sub;


SELECT 	vtm.insert_properties_helper('Isola 12th '||id, 'isola'::text, 'Isabella draft', 'clone'::text, 1360, 'end'::vtm.interpolation_type, pid::text)
FROM   (
	SELECT 	vtm.insert_properties_helper('Isola 12th '||id, 'isola'::text, 'Isabella draft', 'geom'::text, 1150, 'start'::vtm.interpolation_type, ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Transform(geom,4326)),3))) as pid,
			id as id
	FROM	"data_draft_idl"."xiisec_isl" as t
	) as sub;


SELECT 	vtm.insert_properties_helper('Canal 1360 '||id, 'canal'::text, 'Isabella draft', 'clone'::text, 1808, 'end'::vtm.interpolation_type, pid::text)
FROM   (
	SELECT 	vtm.insert_properties_helper('Canal 1360 '||id, 'canal'::text, 'Isabella draft', 'geom'::text, 1360, 'start'::vtm.interpolation_type, ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Transform(geom,4326)),3))) as pid,
			id as id
	FROM	"data_draft_idl"."1360_can" as t
	) as sub;


SELECT 	vtm.insert_properties_helper('Canal 12th '||id, 'canal'::text, 'Isabella draft', 'clone'::text, 1360, 'end'::vtm.interpolation_type, pid::text)
FROM   (
	SELECT 	vtm.insert_properties_helper('Canal 12th '||id, 'canal'::text, 'Isabella draft', 'geom'::text, 1150, 'start'::vtm.interpolation_type, ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Transform(geom,4326)),3))) as pid,
			id as id
	FROM	"data_draft_idl"."xiisec_can" as t
	) as sub;


	SELECT 	vtm.insert_properties_helper('Building 1808 '||id, 'building'::text, 'Isabella draft', 'geom'::text, 1808, 'start'::vtm.interpolation_type, ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Transform(geom,4326)),3))) as pid,
			id as id
	FROM	"data_draft_idl"."1808_un_vol" as t;


SELECT 	vtm.insert_properties_helper('Building 1360 '||id, 'building'::text, 'Isabella draft', 'clone'::text, 1808, 'end'::vtm.interpolation_type, pid::text)
FROM   (
	SELECT 	vtm.insert_properties_helper('Building 1360 '||id, 'building'::text, 'Isabella draft', 'geom'::text, 1360, 'start'::vtm.interpolation_type, ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Transform(geom,4326)),3))) as pid,
			id as id
	FROM	"data_draft_idl"."1360_un_vol" as t
	) as sub;


SELECT 	vtm.insert_properties_helper('Building 13th '||id, 'building'::text, 'Isabella draft', 'clone'::text, 1360, 'end'::vtm.interpolation_type, pid::text)
FROM   (
	SELECT 	vtm.insert_properties_helper('Building 13th '||id, 'building'::text, 'Isabella draft', 'geom'::text, 1250, 'start'::vtm.interpolation_type, ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Transform(geom,4326)),3))) as pid,
			id as id
	FROM	"data_draft_idl"."13th_un_vol" as t
	) as sub;


SELECT 	vtm.insert_properties_helper('Building 12th '||id, 'building'::text, 'Isabella draft', 'clone'::text, 1250, 'end'::vtm.interpolation_type, pid::text)
FROM   (
	SELECT 	vtm.insert_properties_helper('Building 12th '||id, 'building'::text, 'Isabella draft', 'geom'::text, 1150, 'start'::vtm.interpolation_type, ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Transform(geom,4326)),3))) as pid,
			id as id
	FROM	"data_draft_idl"."xiisec_un_vol" as t
	) as sub;



/*******************************/
/* RELATIONS                   */
/*******************************/

/* ALGORITHM 1 : merge when there is no change at all */
/*
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
*/

/* ALGORITHM 2 : merge when there is only a small change */
/*
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
*/