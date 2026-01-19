MAP MODEL V5.0

Goal: see if chi can be found independently of radius by fitting the equation
with delta_1 and delta_2 as the two fit parameters

files copied from model v4.0:
- single_var_model_fits.py
    - modified to use delta1 and delta2 as fit params

data to include in the output file:
- for each run:
    - guess
      - delta1
      - delta2
    - fit results
      - delta1 - value
      - delta2 - value
      - chi (calculated)
      - r (calculated)
    - cov matrix
      - cov_aa
      - cov_ab
      - cov_ba
      - cov_bb
    - SE of:
      - delta1
      - delta2
    - MSE
    - r^2
    - "fit error?"
- final fit data file (results of the fit) - eventually. need to look at uncertainty of fit too at each timepoint
  - for each timepoint:
    - time point
    - data value
    - fit y value
    - fit error1 value (low)
    - fit error2 value (high)
