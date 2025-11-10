CREATE_DR7_VIEW = '''
CREATE MATERIALIZED VIEW IF NOT EXISTS dr7_view AS
SELECT
  warehouse_id, product_id, account_id,
  AVG(qty) FILTER (WHERE dt >= CURRENT_DATE - INTERVAL '7 day') AS dr7
FROM sales_fact
GROUP BY warehouse_id, product_id, account_id;
''';

REFRESH_DR7_VIEW = 'REFRESH MATERIALIZED VIEW CONCURRENTLY dr7_view;';

STOCK_OVERVIEW_SQL = '''
WITH last_stock AS (
  SELECT DISTINCT ON (account_id, warehouse_id, product_id)
         account_id, warehouse_id, product_id, ts, on_hand, inbound, reserved
  FROM stock_snapshot
  ORDER BY account_id, warehouse_id, product_id, ts DESC
), doc_calc AS (
  SELECT ls.account_id, ls.warehouse_id, ls.product_id,
         ls.on_hand, ls.inbound, ls.reserved,
         COALESCE(d.dr7, 0) AS dr7,
         CASE WHEN COALESCE(d.dr7,0) = 0 THEN NULL ELSE ls.on_hand / d.dr7 END AS doc_days
  FROM last_stock ls
  LEFT JOIN dr7_view d
    ON d.account_id = ls.account_id AND d.warehouse_id = ls.warehouse_id AND d.product_id = ls.product_id
)
SELECT * FROM doc_calc
WHERE (:aids IS NULL OR account_id = ANY(:aids))
  AND (:wids IS NULL OR warehouse_id = ANY(:wids))
  AND (:pids IS NULL OR product_id = ANY(:pids));
''';
