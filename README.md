# Identify and remove border effect from DOD

This is an perimental plugin


## Process

1. Find changes
   1. Find threshold q3 + 2 * iqr (same + or -)
   2. Extract those values from DOD
   3. Polygonize the result
   4. Extract the changes (DN = 1)
   5. Delete holes (the small area inside polygons)
   6. Compute area
   7. Compute roundness
   8. Filter by area and roundness -> output
2. Compute slope parameter
   1. Compute some slope parameter from r.texture
   2. Create mask based on thresholds
   3. Polygonize it
   4. Extract non-slope areas (DN = 0)
   5. Delete holes (0.01)
3. Create final mask
   1. Difference between slope mask and identified changes
   2. Merge the difference result and the identified change
4. Clip DOD by the mask

## Get parameters for batch processing

If you have lot a of file to process, you probably may want to use a [batch
process](https://docs.qgis.org/3.28/en/docs/user_manual/processing/batch.html).
The repo contain a tool that allows you to generate a `.json` parameter file
that can be load in the batch processing tool of QGIS.

For the tool to work, your files need to be sorted by directory of places in a
directory and each file should contain years in the format `YYYY_YYYY`. Look at
the example :

```
.
├── Katlahraun
│   ├── Katlahraun_2015_2016_DOD_mask_cordon.tif
│   ├── Katlahraun_2016_2017_DOD_mask_cordon.tif
│   ├── Katlahraun_2017_2018_DOD_mask_cordon.tif
│   ├── Katlahraun_2018_2019_DOD_mask_cordon.tif
│   ├── Katlahraun_2019_2021_DOD_mask_cordon.tif
│   ├── Katlahraun_2021_2022_DOD_mask_cordon.tif
│   └── Katlahraun_2022_2023_DOD_mask_cordon.tif
├── Kerling
│   ├── Kerling_2015_2016_DOD_mask_cordon.tif
│   ├── Kerling_2016_2017_DOD_mask_cordon.tif
│   ├── Kerling_2017_2018_DOD_mask_cordon.tif
│   ├── Kerling_2018_2021_DOD_mask_cordon.tif
│   ├── Kerling_2021_2022_DOD_mask_cordon.tif
│   └── Kerling_2022_2023_DOD_mask_cordon.tif
```

If you have a similar directory, you can run a similar command in your
terminal (run it at the root of the repo) : 

```shell
python -m param_gen.gen_param "input/dir/DODs" "output/dir/results" "param_gen/params.json" --years 2015_2016 --places Site_1 Site_2
```

For a quick help :

```shell
python -m param_gen.gen_param -h
```

By default, `--year` is `None` so as `--places`, they are optional.

