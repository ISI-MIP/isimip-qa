These filed are created using:

```bash
cdo -s outputtab,date,value,nohead -fldmean testing/datasets/linear.nc > testing/cdo/linear_fldmean.csv
cdo -s outputtab,date,value,nohead -fldmean testing/datasets/mask.nc > testing/cdo/mask_fldmean.csv
cdo -s outputtab,date,value,nohead -fldmean testing/datasets/point.nc > testing/cdo/point_fldmean.csv
cdo -s outputtab,date,value,nohead -fldmean testing/datasets/sine.nc > testing/cdo/sine_fldmean.csv
```
