# MANUAL REVIEW REQUIRED
# Reason: Complex RETAIN+BY+FIRST pattern
# data summary;
#     set raw_data;
#     where age > 18;
#     by region;
#     retain running_total 0;
#     running_total + sales;
#     if first.region then running_total = sales;
#     monthly_avg = sales / 30;
# run;
# 
