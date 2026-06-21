data want;
    set have;
    if age > 18 then adult = 1;
run;
