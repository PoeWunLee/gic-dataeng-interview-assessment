WITH bond_ref AS (
	SELECT 
		bp.DATETIME,
		br.ISIN, 
		br.SEDOL, 
		bp.PRICE
	FROM bond_prices bp
	JOIN bond_reference br ON br.ISIN=bp.ISIN
),
equity_ref_extracted_dateparts AS (
	SELECT *,
		SUBSTR(ep.DATETIME, -4) AS YEAR, 
		CASE 
			WHEN CAST(SUBSTR(ep.DATETIME, 1,INSTR(ep.DATETIME , '/')-1) AS INT) <10 THEN '0' || SUBSTR(ep.DATETIME, 1,INSTR(ep.DATETIME , '/')-1)
			ELSE SUBSTR(ep.DATETIME, 1,INSTR(ep.DATETIME , '/')-1)
		END
		 AS MONTH, 
		 CASE 
		 	 WHEN CAST(SUBSTR(ep.DATETIME, INSTR(ep.DATETIME , '/')+1, INSTR(SUBSTR(ep.DATETIME, INSTR(ep.DATETIME , '/')+1), '/')-1) AS INT) <10 THEN '0' ||  SUBSTR(ep.DATETIME, INSTR(ep.DATETIME , '/')+1, INSTR(SUBSTR(ep.DATETIME, INSTR(ep.DATETIME , '/')+1), '/')-1)
		 	 ELSE SUBSTR(ep.DATETIME, INSTR(ep.DATETIME , '/')+1, INSTR(SUBSTR(ep.DATETIME, INSTR(ep.DATETIME , '/')+1), '/')-1)
		 END as DAY
	FROM equity_prices ep
),
equity_ref AS (
	SELECT 
		YEAR || '-' || MONTH || '-' || DAY as "DATETIME", 
		SYMBOL,
		PRICE
	FROM equity_ref_extracted_dateparts
),
consol_recon_cte as (
    SELECT 
        bf.DATETIME, 
        bf.FUND,bf."FINANCIAL TYPE" AS 'INSTRUMENT_TYPE',
        bref."SECURITY NAME" AS 'SECURITY_NAME',   
        bf.ISIN as IDENTIFIER,
        'ISIN' as IDENTIFIER_TYPE,
        bf.PRICE AS PRICE_FUND, 
        bpref.PRICE PRICE_REF,
        bf.PRICE - bpref.PRICE as DIFF_PRICE_REF
    FROM fund_position bf
    JOIN bond_ref bpref ON bpref.ISIN=bf.ISIN AND bf.DATETIME=bpref.DATETIME
    JOIN bond_reference bref on bref.ISIN=bf.ISIN
    WHERE bf.ISIN IS NOT NULL
    UNION ALL
    SELECT 
        bf.DATETIME,
        bf.FUND,
        bf."FINANCIAL TYPE" AS 'INSTRUMENT_TYPE',
        bref."SECURITY NAME" AS 'SECURITY_NAME',    
        bf.SEDOL AS IDENTIFIER,
        'CUSIP' AS IDENTIFIER_TYPE,
        bf.PRICE PRICE_FUND, 
        bpref.PRICE PRICE_REF,
        bf.PRICE - bpref.PRICE as DIFF_PRICE_REF
    FROM fund_position bf
    JOIN bond_ref bpref ON bpref.SEDOL=bf.SEDOL AND bf.DATETIME=bpref.DATETIME
    JOIN bond_reference bref ON bref.SEDOL=bf.SEDOL
    WHERE bf.SEDOL IS NOT NULL
    UNION ALL
    SELECT 
        ef.DATETIME,
        ef.FUND,
        ef."FINANCIAL TYPE" AS 'INSTRUMENT_TYPE',
        eref."SECURITY NAME" AS 'SECURITY_NAME',  
        ef.SYMBOL AS IDENTIFIER,
        'SYMBOL' AS IDENTIFIER_TYPE,
        ef.PRICE PRICE_FUND, 
        epref.PRICE PRICE_REF,
        ef.PRICE - epref.PRICE as DIFF_PRICE_REF
    FROM fund_position ef
    JOIN equity_ref epref ON ef.SYMBOL=epref.SYMBOL AND ef.DATETIME=epref.DATETIME
    JOIN equity_reference eref ON eref.SYMBOL=ef.SYMBOL
    WHERE ef.SYMBOL IS NOT NULL
)
SELECT 
    DATETIME, 
    FUND, 
    sum(DIFF_PRICE_REF) as DIFF_FROM_REF
FROM consol_recon_cte 
GROUP BY 1,2
ORDER BY 1,2
;