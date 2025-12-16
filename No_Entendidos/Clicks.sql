-- Clicks

WITH fecha as (
SELECT
cast('2025-06-01 00:00:00' as timestamp) as fecha_inicio,
cast('2025-07-01 00:00:00' as timestamp) as fecha_fin
), intents as (
	SELECT ts,
		id,
		session_id,
		message_id,
		message,
		results_intent_name,
		results_intent_id,
		parent_intent_id,
		parent_intent_name,
		model_type,
		results_showable,
		results_score as score,
		rule_id,
		(
			CASE
				WHEN (
					parent_intent_id IS NOT NULL
					AND parent_intent_id != ''
				) THEN parent_intent_id ELSE results_intent_id
			END
		) mostrado,
		(
			CASE
				WHEN (
					parent_intent_name IS NOT NULL
					AND parent_intent_name != ''
				) THEN parent_intent_name ELSE results_intent_name
			END
		) mostrado_name
	FROM boti_intent_search
	left join fecha on 1=1
	WHERE ts >= fecha_inicio
		and ts <= fecha_fin
)
SELECT a.*,
	b.ts response_ts,
	b.response_message,
	b.response_intent_id
FROM intents a
    LEFT JOIN fecha on 1=1
	LEFT JOIN boti_intent_search_response b ON a.id = b.id
	AND b.ts >= fecha_inicio
	and b.ts <= fecha_fin
ORDER BY a.ts DESC
