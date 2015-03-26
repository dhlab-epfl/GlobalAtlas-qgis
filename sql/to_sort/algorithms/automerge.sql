/* ALGORITHM 1 : merge when there is no change at all */

UPDATE vtm.events as e1
SET entity_id = e2.entity_id
FROM vtm.events as e2
WHERE e1.key='geom' AND e2.key='geom' AND e1.id<e2.id AND ST_Equals(e1.geovalue,e2.geovalue);



/* ALGORITHM 2 : merge when there is only a small change */

UPDATE vtm.events as e1
SET entity_id = e2.entity_id
FROM vtm.events as e2
WHERE 	e1.key = 'geom'
		AND 	
	 	e2.key = 'geom'
		AND
		e1.id<e2.id
		AND
		ST_IsValid(e1.geovalue)
		AND
		ST_IsValid(e2.geovalue)
		AND
		ST_Intersects(e1.geovalue, e2.geovalue)
		AND
		ST_Area( ST_Intersection(e1.geovalue,e2.geovalue) ) > 0.95*GREATEST(ST_Area( e1.geovalue),ST_Area( e2.geovalue));


/* ALGORITHM 3 : set succession relation for entities that overlap */
-- can be very long (around 10 minutes for now)
INSERT INTO vtm.related_entities(a_id, b_id)
SELECT 	evA.entity_id as a_id,
		evB.entity_id as b_id
FROM 	vtm.events as evA
JOIN 	vtm.events as evB 		ON 		ST_Intersects(evA.geovalue, evB.geovalue)
JOIN 	vtm.entities as entA	ON 		evA.entity_id = entA.id
JOIN 	vtm.entities as entB	ON 		evB.entity_id = entB.id
WHERE 	entA.type_id=entB.type_id AND evA.id<>evB.id AND evA.date<>evB.date;





/* CLEANUP 1 : remove unused entities */

DELETE FROM vtm.entities as e
WHERE (
	SELECT COUNT(*)
	FROM vtm.events 
	WHERE entity_id = e.id
) = 0;