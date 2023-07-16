# Identify and remove border effect from DOD

**Still under development**


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


## The parameter generator utils

