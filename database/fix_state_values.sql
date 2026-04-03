-- Fix malformed state values in existing data
-- Handles "state_xxx" prefixes and multi-state comma-separated values

-- 1. Fix "state_xxx" patterns → proper state names
UPDATE classifications SET state = 'Delhi'            WHERE state = 'state_delhi';
UPDATE classifications SET state = 'Kerala'            WHERE state = 'state_kerala';
UPDATE classifications SET state = 'Meghalaya'         WHERE state = 'state_meghalaya';
UPDATE classifications SET state = 'Nagaland'          WHERE state = 'state_nagaland';
UPDATE classifications SET state = 'Uttar Pradesh'     WHERE state = 'state_uttar_pradesh';
UPDATE classifications SET state = 'Uttarakhand'       WHERE state = 'state_uttarakhand';
-- Catch any remaining "state_" prefixes generically
UPDATE classifications SET state = initcap(replace(substring(state from 7), '_', ' '))
  WHERE state LIKE 'state\_%';

-- 2. Fix lowercase-only values
UPDATE classifications SET state = 'Kerala' WHERE state = 'kerala';

-- 3. Multi-state values → keep first state only
UPDATE classifications SET state = trim(split_part(state, ',', 1))
  WHERE state LIKE '%,%';

-- Mirror the same fixes to the denormalised news_events table
UPDATE news_events SET state = c.state
  FROM classifications c
  WHERE news_events.classification_id = c.id
    AND news_events.state IS DISTINCT FROM c.state;
