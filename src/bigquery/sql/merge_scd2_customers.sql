-- BigQuery DML: Slowly Changing Dimension Type 2 (SCD2) MERGE for DIM_CUSTOMERS

MERGE INTO `{project_id}.{dataset_id}.dim_customers` T
USING (
  SELECT
    NK_Customer_Number AS join_key,
    *
  FROM `{project_id}.{dataset_id}.stg_customers`

  UNION ALL

  SELECT
    NULL AS join_key,
    S.*
  FROM `{project_id}.{dataset_id}.stg_customers` S
  JOIN `{project_id}.{dataset_id}.dim_customers` T
    ON S.NK_Customer_Number = T.NK_Customer_Number
   AND T.Is_Current_Flag = TRUE
   AND (
     S.First_Name != T.First_Name OR
     S.Last_Name != T.Last_Name OR
     S.Email != T.Email OR
     S.Customer_Segment != T.Customer_Segment
   )
) S
ON T.NK_Customer_Number = S.join_key

-- Expire existing current record when attribute changes
WHEN MATCHED AND T.Is_Current_Flag = TRUE AND (
     T.First_Name != S.First_Name OR
     T.Last_Name != S.Last_Name OR
     T.Email != S.Email OR
     T.Customer_Segment != S.Customer_Segment
   ) THEN
  UPDATE SET
    T.Effective_End_Date = S.Effective_Start_Date,
    T.Is_Current_Flag = FALSE

-- Insert new current version
WHEN NOT MATCHED THEN
  INSERT (
    SK_Customer_Id, NK_Customer_Number, First_Name, Last_Name, Email,
    Customer_Segment, Effective_Start_Date, Effective_End_Date, Is_Current_Flag
  )
  VALUES (
    S.SK_Customer_Id, S.NK_Customer_Number, S.First_Name, S.Last_Name, S.Email,
    S.Customer_Segment, S.Effective_Start_Date, NULL, TRUE
  );
