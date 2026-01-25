import pandas as pd

def reconciliation_analysis(recon_df:pd.DataFrame)->pd.DataFrame:
    #process
    ## 1. summary recon at fund level 
    recon_df_agg = recon_df.copy()
    recon_df_agg = recon_df_agg[["DATETIME", "FUND", "PRICE_FUND", "PRICE_REF"]]\
                                    .groupby(["DATETIME", "FUND",])\
                                        .sum()\
                                            .reset_index()
    
    ## 2. breakdown on which ticker/identifier do not reconcile. Useful for troubleshooting context.
    recon_df_breakdown = recon_df.copy()
    recon_df_breakdown["DIFF_FROM_REF"] = recon_df_breakdown["PRICE_FUND"]-recon_df_breakdown["PRICE_REF"]
    recon_df_breakdown = recon_df_breakdown.loc[recon_df_breakdown["PRICE_FUND"]!=recon_df_breakdown["PRICE_REF"]]

    return recon_df_agg, recon_df_breakdown

def highest_performing_by_mth(performance_df:pd.DataFrame)->pd.DataFrame:
    # no further processing in application layer required. scope of requirement fulfilled in query within CTE logic 
    # placeholder function for potential expandsion of requirements (e.g.parameterised date ranges)
    return performance_df