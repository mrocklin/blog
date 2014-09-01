---
layout: post
title: Introducing Blaze - Practice
tagline: in which we solve a real problem
category : work
draft : true
tags : [scipy, Python, Programming]
---
{% include JB/setup %}


We look at data from the [Home Mortgage Disclosure
Act](http://www.ffiec.gov/hmda/), a collection of actions taken on
housing loans by various governmental agencies (gzip-ed csv file
[here](http://files.consumerfinance.gov/hmda/hmda_lar-2012.csv.gz))
(thanks to [Aron Ahmadia](http://aron.ahmadia.net/) for the pointer).
Uncompressed this dataset is around 10GB on disk and so we don't want to
load it up into memory with a modern commercial notebook.

Instead, we use Blaze to investigate the data, select down to the data
we care about, and then migrate that data into a suitable computational
backend.

In this post we're going to use the interactive `Table` object, which
wraps up a dataset and calls compute whenever we ask for something to be
printed to the screen. It retains the abstract delayed-evaluation nature
of Blaze with the interactive feel of NumPy and Pandas.

{% highlight Python %}
from blaze import CSV, Table
csv = CSV('hmda_lar-2012.csv')  # Open the CSV file
t = Table(csv)                  # Interact with CSV file using interactive Table object
t
{% endhighlight %}

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>action_taken</th>
      <th>action_taken_name</th>
      <th>agency_code</th>
      <th>agency_abbr</th>
      <th>agency_name</th>
      <th>applicant_ethnicity</th>
      <th>applicant_ethnicity_name</th>
      <th>applicant_income_000s</th>
      <th>applicant_race_1</th>
      <th>applicant_race_2</th>
      <th>applicant_race_3</th>
      <th>applicant_race_4</th>
      <th>applicant_race_5</th>
      <th>applicant_race_name_1</th>
      <th>applicant_race_name_2</th>
      <th>applicant_race_name_3</th>
      <th>applicant_race_name_4</th>
      <th>applicant_race_name_5</th>
      <th>applicant_sex</th>
      <th>applicant_sex_name</th>
      <th>application_date_indicator</th>
      <th>as_of_year</th>
      <th>census_tract_number</th>
      <th>co_applicant_ethnicity</th>
      <th>co_applicant_ethnicity_name</th>
      <th>co_applicant_race_1</th>
      <th>co_applicant_race_2</th>
      <th>co_applicant_race_3</th>
      <th>co_applicant_race_4</th>
      <th>co_applicant_race_5</th>
      <th>co_applicant_race_name_1</th>
      <th>co_applicant_race_name_2</th>
      <th>co_applicant_race_name_3</th>
      <th>co_applicant_race_name_4</th>
      <th>co_applicant_race_name_5</th>
      <th>co_applicant_sex</th>
      <th>co_applicant_sex_name</th>
      <th>county_code</th>
      <th>county_name</th>
      <th>denial_reason_1</th>
      <th>denial_reason_2</th>
      <th>denial_reason_3</th>
      <th>denial_reason_name_1</th>
      <th>denial_reason_name_2</th>
      <th>denial_reason_name_3</th>
      <th>edit_status</th>
      <th>edit_status_name</th>
      <th>hoepa_status</th>
      <th>hoepa_status_name</th>
      <th>lien_status</th>
      <th>lien_status_name</th>
      <th>loan_purpose</th>
      <th>loan_purpose_name</th>
      <th>loan_type</th>
      <th>loan_type_name</th>
      <th>msamd</th>
      <th>msamd_name</th>
      <th>owner_occupancy</th>
      <th>owner_occupancy_name</th>
      <th>preapproval</th>
      <th>preapproval_name</th>
      <th>property_type</th>
      <th>property_type_name</th>
      <th>purchaser_type</th>
      <th>purchaser_type_name</th>
      <th>respondent_id</th>
      <th>sequence_number</th>
      <th>state_code</th>
      <th>state_abbr</th>
      <th>state_name</th>
      <th>hud_median_family_income</th>
      <th>loan_amount_000s</th>
      <th>number_of_1_to_4_family_units</th>
      <th>number_of_owner_occupied_units</th>
      <th>minority_population</th>
      <th>population</th>
      <th>rate_spread</th>
      <th>tract_to_msamd_income</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0 </th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 7</td>
      <td>  HUD</td>
      <td> Department of Housing and Urban Development</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 173</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>           Male</td>
      <td> 0</td>
      <td> 2012</td>
      <td> 8803.06</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>           White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 2</td>
      <td>          Female</td>
      <td> 197</td>
      <td>      Will County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 3</td>
      <td>      Refinancing</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td> 16974</td>
      <td>            Chicago, Joliet, Naperville - IL</td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 6</td>
      <td> Commercial bank, savings bank or savings assoc...</td>
      <td> 36-4176531</td>
      <td>    2712</td>
      <td> 17</td>
      <td> IL</td>
      <td>  Illinois</td>
      <td> 77300</td>
      <td> 264</td>
      <td> 2153</td>
      <td> 1971</td>
      <td> 45.820000</td>
      <td> 7894</td>
      <td>  NaN</td>
      <td> 170.679993</td>
    </tr>
    <tr>
      <th>1 </th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 5</td>
      <td> NCUA</td>
      <td>        National Credit Union Administration</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td>  83</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>           Male</td>
      <td> 0</td>
      <td> 2012</td>
      <td> 2915.00</td>
      <td> 5</td>
      <td>        No co-applicant</td>
      <td> 8</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> No co-applicant</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 5</td>
      <td> No co-applicant</td>
      <td> 111</td>
      <td>   Midland County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 3</td>
      <td>      Refinancing</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td>   NaN</td>
      <td>                                            </td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 0</td>
      <td> Loan was not originated or was not sold in cal...</td>
      <td> 0000060137</td>
      <td>     328</td>
      <td> 26</td>
      <td> MI</td>
      <td>  Michigan</td>
      <td> 52100</td>
      <td> 116</td>
      <td> 1662</td>
      <td> 1271</td>
      <td>  3.340000</td>
      <td> 4315</td>
      <td>  NaN</td>
      <td> 102.760002</td>
    </tr>
    <tr>
      <th>2 </th>
      <td> 6</td>
      <td> Loan purchased by the institution</td>
      <td> 9</td>
      <td> CFPB</td>
      <td>        Consumer Financial Protection Bureau</td>
      <td> 4</td>
      <td>         Not applicable</td>
      <td>  70</td>
      <td> 7</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>            Not applicable</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 4</td>
      <td> Not applicable</td>
      <td> 2</td>
      <td> 2012</td>
      <td>  212.01</td>
      <td> 4</td>
      <td>         Not applicable</td>
      <td> 7</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>  Not applicable</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 4</td>
      <td>  Not applicable</td>
      <td>   7</td>
      <td>    Benton County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>  6</td>
      <td> Quality edit failure only</td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 4</td>
      <td>          Not applicable</td>
      <td> 3</td>
      <td>      Refinancing</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td> 22220</td>
      <td>   Fayetteville, Springdale, Rogers - AR, MO</td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 8</td>
      <td>                             Affiliate institution</td>
      <td> 0000476810</td>
      <td>   43575</td>
      <td>  5</td>
      <td> AR</td>
      <td>  Arkansas</td>
      <td> 58200</td>
      <td> 159</td>
      <td> 1194</td>
      <td>  708</td>
      <td> 21.870001</td>
      <td> 4239</td>
      <td>  NaN</td>
      <td> 127.639999</td>
    </tr>
    <tr>
      <th>3 </th>
      <td> 6</td>
      <td> Loan purchased by the institution</td>
      <td> 9</td>
      <td> CFPB</td>
      <td>        Consumer Financial Protection Bureau</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 108</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 2</td>
      <td>         Female</td>
      <td> 2</td>
      <td> 2012</td>
      <td>  407.06</td>
      <td> 5</td>
      <td>        No co-applicant</td>
      <td> 8</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> No co-applicant</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 5</td>
      <td> No co-applicant</td>
      <td> 123</td>
      <td>    Ramsey County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 4</td>
      <td>          Not applicable</td>
      <td> 3</td>
      <td>      Refinancing</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td> 33460</td>
      <td> Minneapolis, St. Paul, Bloomington - MN, WI</td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 1</td>
      <td>                                 Fannie Mae (FNMA)</td>
      <td> 0000451965</td>
      <td> 2374657</td>
      <td> 27</td>
      <td> MN</td>
      <td> Minnesota</td>
      <td> 83900</td>
      <td> 100</td>
      <td> 1927</td>
      <td> 1871</td>
      <td> 13.680000</td>
      <td> 4832</td>
      <td>  NaN</td>
      <td> 137.669998</td>
    </tr>
    <tr>
      <th>4 </th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 3</td>
      <td> FDIC</td>
      <td>       Federal Deposit Insurance Corporation</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> NaN</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>           Male</td>
      <td> 0</td>
      <td> 2012</td>
      <td>  104.00</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>           White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 2</td>
      <td>          Female</td>
      <td>   3</td>
      <td>     Allen County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>  6</td>
      <td> Quality edit failure only</td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 2</td>
      <td> Home improvement</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td> 23060</td>
      <td>                             Fort Wayne - IN</td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 0</td>
      <td> Loan was not originated or was not sold in cal...</td>
      <td> 0000013801</td>
      <td>      11</td>
      <td> 18</td>
      <td> IN</td>
      <td>   Indiana</td>
      <td> 63800</td>
      <td> 267</td>
      <td> 1309</td>
      <td> 1160</td>
      <td>  4.680000</td>
      <td> 3612</td>
      <td>  NaN</td>
      <td> 139.100006</td>
    </tr>
    <tr>
      <th>5 </th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 7</td>
      <td>  HUD</td>
      <td> Department of Housing and Urban Development</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 144</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>           Male</td>
      <td> 0</td>
      <td> 2012</td>
      <td> 8057.01</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>           White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>            Male</td>
      <td>  31</td>
      <td>      Cook County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 3</td>
      <td>      Refinancing</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td> 16974</td>
      <td>            Chicago, Joliet, Naperville - IL</td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 3</td>
      <td>                               Freddie Mac (FHLMC)</td>
      <td> 36-4327855</td>
      <td>   22594</td>
      <td> 17</td>
      <td> IL</td>
      <td>  Illinois</td>
      <td> 77300</td>
      <td> 260</td>
      <td> 1390</td>
      <td> 1700</td>
      <td>  6.440000</td>
      <td> 5074</td>
      <td>  NaN</td>
      <td> 140.550003</td>
    </tr>
    <tr>
      <th>6 </th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 7</td>
      <td>  HUD</td>
      <td> Department of Housing and Urban Development</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td>  51</td>
      <td> 3</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> Black or African American</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>           Male</td>
      <td> 0</td>
      <td> 2012</td>
      <td>   17.00</td>
      <td> 5</td>
      <td>        No co-applicant</td>
      <td> 8</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> No co-applicant</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 5</td>
      <td> No co-applicant</td>
      <td>  19</td>
      <td> Calcasieu Parish</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 1</td>
      <td>    Home purchase</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td> 29340</td>
      <td>                           Lake Charles - LA</td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 1</td>
      <td>                                 Fannie Mae (FNMA)</td>
      <td> 7056000000</td>
      <td>   34177</td>
      <td> 22</td>
      <td> LA</td>
      <td> Louisiana</td>
      <td> 62400</td>
      <td> 115</td>
      <td> 3500</td>
      <td> 2797</td>
      <td> 29.260000</td>
      <td> 8745</td>
      <td>  NaN</td>
      <td>  86.739998</td>
    </tr>
    <tr>
      <th>7 </th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 7</td>
      <td>  HUD</td>
      <td> Department of Housing and Urban Development</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 162</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>           Male</td>
      <td> 0</td>
      <td> 2012</td>
      <td>    2.01</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>           White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 2</td>
      <td>          Female</td>
      <td>  49</td>
      <td>     Grand County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 3</td>
      <td>      Refinancing</td>
      <td> 2</td>
      <td>   FHA-insured</td>
      <td>   NaN</td>
      <td>                                            </td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 6</td>
      <td> Commercial bank, savings bank or savings assoc...</td>
      <td> 87-0623581</td>
      <td>    2141</td>
      <td>  8</td>
      <td> CO</td>
      <td>  Colorado</td>
      <td> 61000</td>
      <td> 283</td>
      <td> 5706</td>
      <td> 1724</td>
      <td>  9.650000</td>
      <td> 4817</td>
      <td>  NaN</td>
      <td> 128.559998</td>
    </tr>
    <tr>
      <th>8 </th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 3</td>
      <td> FDIC</td>
      <td>       Federal Deposit Insurance Corporation</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td>  32</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 2</td>
      <td>         Female</td>
      <td> 0</td>
      <td> 2012</td>
      <td>  103.04</td>
      <td> 5</td>
      <td>        No co-applicant</td>
      <td> 8</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> No co-applicant</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 5</td>
      <td> No co-applicant</td>
      <td>   3</td>
      <td>     Allen County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 3</td>
      <td>      Refinancing</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td> 23060</td>
      <td>                             Fort Wayne - IN</td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 0</td>
      <td> Loan was not originated or was not sold in cal...</td>
      <td> 0000013801</td>
      <td>      10</td>
      <td> 18</td>
      <td> IN</td>
      <td>   Indiana</td>
      <td> 63800</td>
      <td>  40</td>
      <td> 2384</td>
      <td> 2210</td>
      <td>  6.640000</td>
      <td> 6601</td>
      <td> 3.33</td>
      <td> 149.690002</td>
    </tr>
    <tr>
      <th>9 </th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 9</td>
      <td> CFPB</td>
      <td>        Consumer Financial Protection Bureau</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td>  38</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>           Male</td>
      <td> 0</td>
      <td> 2012</td>
      <td> 9608.00</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>           White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 2</td>
      <td>          Female</td>
      <td>  41</td>
      <td>    Talbot County</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 3</td>
      <td>      Refinancing</td>
      <td> 1</td>
      <td>  Conventional</td>
      <td>   NaN</td>
      <td>                                            </td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 3</td>
      <td>                               Freddie Mac (FHLMC)</td>
      <td> 0000504713</td>
      <td>   18459</td>
      <td> 24</td>
      <td> MD</td>
      <td>  Maryland</td>
      <td> 72600</td>
      <td> 108</td>
      <td> 1311</td>
      <td>  785</td>
      <td>  6.040000</td>
      <td> 1920</td>
      <td>  NaN</td>
      <td>  77.279999</td>
    </tr>
    <tr>
      <th>10</th>
      <td> 1</td>
      <td>                   Loan originated</td>
      <td> 7</td>
      <td>  HUD</td>
      <td> Department of Housing and Urban Development</td>
      <td> 2</td>
      <td> Not Hispanic or Latino</td>
      <td>  47</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>                     White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 1</td>
      <td>           Male</td>
      <td> 0</td>
      <td> 2012</td>
      <td>   22.04</td>
      <td> 1</td>
      <td>     Hispanic or Latino</td>
      <td> 5</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>           White</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> 2</td>
      <td>          Female</td>
      <td>  19</td>
      <td> Calcasieu Parish</td>
      <td> None</td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td> </td>
      <td>NaN</td>
      <td>                          </td>
      <td> 2</td>
      <td> Not a HOEPA loan</td>
      <td> 1</td>
      <td> Secured by a first lien</td>
      <td> 1</td>
      <td>    Home purchase</td>
      <td> 3</td>
      <td> VA-guaranteed</td>
      <td> 29340</td>
      <td>                           Lake Charles - LA</td>
      <td> 1</td>
      <td> Owner-occupied as a principal dwelling</td>
      <td> 3</td>
      <td> Not applicable</td>
      <td> 1</td>
      <td> One-to-four family dwelling (other than manufa...</td>
      <td> 6</td>
      <td> Commercial bank, savings bank or savings assoc...</td>
      <td> 7056000000</td>
      <td>   33791</td>
      <td> 22</td>
      <td> LA</td>
      <td> Louisiana</td>
      <td> 62400</td>
      <td> 158</td>
      <td> 1854</td>
      <td> 1463</td>
      <td> 12.410000</td>
      <td> 4955</td>
      <td>  NaN</td>
      <td> 112.010002</td>
    </tr>
  </tbody>
</table>

Reducing the Dataset
--------------------

That's a lot of columns, most of which are redundant or don't carry much
information. Let's clean up our dataset a bit by selecting a smaller
subset of columns. Already this quick investigation improves our
comprehension and reduces the size of the dataset.

{% highlight Python %}
columns = ['action_taken_name', 'agency_abbr', 'applicant_ethnicity_name',
           'applicant_race_name_1', 'applicant_sex_name', 'county_name',
           'loan_purpose_name', 'state_abbr']

t = t[columns]
t
{% endhighlight %}

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>action_taken_name</th>
      <th>agency_abbr</th>
      <th>applicant_ethnicity_name</th>
      <th>applicant_race_name_1</th>
      <th>applicant_sex_name</th>
      <th>county_name</th>
      <th>loan_purpose_name</th>
      <th>state_abbr</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0 </th>
      <td>                   Loan originated</td>
      <td>  HUD</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>           Male</td>
      <td>      Will County</td>
      <td>      Refinancing</td>
      <td> IL</td>
    </tr>
    <tr>
      <th>1 </th>
      <td>                   Loan originated</td>
      <td> NCUA</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>           Male</td>
      <td>   Midland County</td>
      <td>      Refinancing</td>
      <td> MI</td>
    </tr>
    <tr>
      <th>2 </th>
      <td> Loan purchased by the institution</td>
      <td> CFPB</td>
      <td>         Not applicable</td>
      <td>            Not applicable</td>
      <td> Not applicable</td>
      <td>    Benton County</td>
      <td>      Refinancing</td>
      <td> AR</td>
    </tr>
    <tr>
      <th>3 </th>
      <td> Loan purchased by the institution</td>
      <td> CFPB</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>         Female</td>
      <td>    Ramsey County</td>
      <td>      Refinancing</td>
      <td> MN</td>
    </tr>
    <tr>
      <th>4 </th>
      <td>                   Loan originated</td>
      <td> FDIC</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>           Male</td>
      <td>     Allen County</td>
      <td> Home improvement</td>
      <td> IN</td>
    </tr>
    <tr>
      <th>5 </th>
      <td>                   Loan originated</td>
      <td>  HUD</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>           Male</td>
      <td>      Cook County</td>
      <td>      Refinancing</td>
      <td> IL</td>
    </tr>
    <tr>
      <th>6 </th>
      <td>                   Loan originated</td>
      <td>  HUD</td>
      <td> Not Hispanic or Latino</td>
      <td> Black or African American</td>
      <td>           Male</td>
      <td> Calcasieu Parish</td>
      <td>    Home purchase</td>
      <td> LA</td>
    </tr>
    <tr>
      <th>7 </th>
      <td>                   Loan originated</td>
      <td>  HUD</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>           Male</td>
      <td>     Grand County</td>
      <td>      Refinancing</td>
      <td> CO</td>
    </tr>
    <tr>
      <th>8 </th>
      <td>                   Loan originated</td>
      <td> FDIC</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>         Female</td>
      <td>     Allen County</td>
      <td>      Refinancing</td>
      <td> IN</td>
    </tr>
    <tr>
      <th>9 </th>
      <td>                   Loan originated</td>
      <td> CFPB</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>           Male</td>
      <td>    Talbot County</td>
      <td>      Refinancing</td>
      <td> MD</td>
    </tr>
    <tr>
      <th>10</th>
      <td>                   Loan originated</td>
      <td>  HUD</td>
      <td> Not Hispanic or Latino</td>
      <td>                     White</td>
      <td>           Male</td>
      <td> Calcasieu Parish</td>
      <td>    Home purchase</td>
      <td> LA</td>
    </tr>
  </tbody>
</table>

More Complex Computation
------------------------

Now that we can more clearly see what's going on let's ask a simple
question:

*How many times does each action occur in the state of New York?*

{% highlight Python %}
t2 = t[t.state_abbr == 'NY']
t2
{% endhighlight %}

{% highlight Python %}
%%time
from blaze import into, by
from pandas import DataFrame
# Group on action_taken_name, count each group
into(DataFrame, by(t2.action_taken_name,
                   t2.action_taken_name.count()).sort('action_taken_name_count',
                                                      ascending=False))
{% endhighlight %}

    CPU times: user 13min 50s, sys: 5.23 s, total: 13min 55s
    Wall time: 13min 55s

<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>action_taken_name</th>
      <th>action_taken_name_count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>                                   Loan originated</td>
      <td> 285106</td>
    </tr>
    <tr>
      <th>1</th>
      <td>       Application denied by financial institution</td>
      <td> 109423</td>
    </tr>
    <tr>
      <th>2</th>
      <td>                 Loan purchased by the institution</td>
      <td>  75241</td>
    </tr>
        <tr>
      <th>3</th>
      <td>                Application withdrawn by applicant</td>
      <td>  50563</td>
    </tr>
    <tr>
      <th>4</th>
      <td>             Application approved but not accepted</td>
      <td>  25632</td>
    </tr>
    <tr>
      <th>5</th>
      <td>                    File closed for incompleteness</td>
      <td>  20585</td>
    </tr>
    <tr>
      <th>6</th>
      <td>     Preapproval request approved but not accepted</td>
      <td>    259</td>
    </tr>
    <tr>
      <th>7</th>
      <td> Preapproval request denied by financial instit...</td>
      <td>    171</td>
    </tr>
  </tbody>
</table>
</div>

Great! Sadly, because it was reading through the CSV file and because it
was using a Pure Python backend, that computation took fourteen minutes.

Moving to a Faster Backend
--------------------------

By default computations on CSV files use the streaming Python backend.
While robust for large files and decently fast, this backend parses the
CSV file each time we do a full-data operation, and this parsing is very
slow. Let's move our reduced dataset to a more efficient and widely
accessible backend, `sqlite`.

{% highlight Python %}
from blaze import SQL
sql = SQL('sqlite:///hmda.db', 'data', schema=t.schema) # A SQLite database
into(sql, t)  # Migrate data
{% endhighlight %}

Yup, a little `sqlite` database just arrived

    $ ls -lh hmda*

    -rw-r--r-- 1 mrocklin mrocklin 2.7G Aug 25 13:38 hmda.db
    -rw-r--r-- 1 mrocklin mrocklin  12G Jul 10 12:15 hmda_lar-2012.csv


Working with SQL
----------------

Now that we've migrated our csv file into a sqlite database let's redefine `t`
to use the SQL backend and repeat our computation.

{% highlight Python %}
# t = Table(csv)
t = Table(sql)
t2 = t[t.state_abbr == 'NY']
{% endhighlight %}

{% highlight Python %}
%%time
into(DataFrame, by(t2.action_taken_name,
                   t2.action_taken_name.count()).sort('action_taken_name_count',
                                                      ascending=False))
{% endhighlight %}

    CPU times: user 5.55 s, sys: 1.64 s, total: 7.19 s
    Wall time: 7.46 s


<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>action_taken_name</th>
      <th>action_taken_name_count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>                                   Loan originated</td>
      <td> 285106</td>
    </tr>
    <tr>
      <th>1</th>
      <td>       Application denied by financial institution</td>
      <td> 109423</td>
    </tr>
    <tr>
      <th>2</th>
      <td>                 Loan purchased by the institution</td>
      <td>  75241</td>
    </tr>
        <tr>
      <th>3</th>
      <td>                Application withdrawn by applicant</td>
      <td>  50563</td>
    </tr>
    <tr>
      <th>4</th>
      <td>             Application approved but not accepted</td>
      <td>  25632</td>
    </tr>
    <tr>
      <th>5</th>
      <td>                    File closed for incompleteness</td>
      <td>  20585</td>
    </tr>
    <tr>
      <th>6</th>
      <td>     Preapproval request approved but not accepted</td>
      <td>    259</td>
    </tr>
    <tr>
      <th>7</th>
      <td> Preapproval request denied by financial instit...</td>
      <td>    171</td>
    </tr>
  </tbody>
</table>
</div>

*We're about to repeat this same computation many times.  We'll omit the table
result from here on out.  It will always be the same.*

Create an index on state name
-----------------------------

This was much faster, largely because the data was stored in a binary
format. We can improve the query speed significantly by placing an index
on the `state_abbr` field. This will cause the selection
`t[t.state_abbr == 'NY']` to return more quickly, eliminating the need
for an expensive full table scan.

{% highlight Python %}
from blaze import create_index
create_index(sql, 'state_abbr', name='state_abbr_index')
{% endhighlight %}

Now we can ask this same query for many states at interactive
timescales.

{% highlight Python %}
t2 = t[t.state_abbr == 'NY']
{% endhighlight %}

{% highlight Python %}
%%time
into(DataFrame, by(t2.action_taken_name,
                   t2.action_taken_name.count()).sort('action_taken_name_count',
                                                      ascending=False))
{% endhighlight %}

    CPU times: user 1.74 s, sys: 430 ms, total: 2.17 s
    Wall time: 2.17 s


Comparing against MongoDB
=========================

Because moving between computational backends is now easy, we can quickly
compare performance between backends. SQLite and MongoDB are similarly
available technologies, each being trivial to set up on a personal computer.
However they're also fairly different technologies with varying communities.

Which performs faster for our sample computation?

{% highlight Python %}
import pymongo
db = pymongo.MongoClient().db

into(db.hmda, sql)  # Migrate to Mongo DB from SQLite database
{% endhighlight %}

{% highlight Python %}
# t = Table(csv)
# t = Table(sql)
t = Table(db.hmda)
{% endhighlight %}

{% highlight Python %}
t2 = t[t.state_abbr == 'NY']
{% endhighlight %}

{% highlight Python %}
%%time
into(DataFrame, by(t2.action_taken_name,
                   t2.action_taken_name.count()).sort('action_taken_name_count',
                                                      ascending=False))
{% endhighlight %}

    CPU times: user 4.05 ms, sys: 701 µs, total: 4.76 ms
    Wall time: 7.61 s

Almost exactly the same time as for SQLite.

We just did a complex thing easily.  If we weren't familiar
with MongoDB we would need to learn how to set up a database, how to migrate
data from SQL to MongoDB, and finally how to perform queries.  Blaze eased that
process *considerably*.

### Create an index on state name

Again we create an index on the state name and observe the performance
difference.

{% highlight Python %}
create_index(db.hmda, 'state_abbr', name='state_abbr_index')
{% endhighlight %}

{% highlight Python %}
t2 = t[t.state_abbr == 'NY']
{% endhighlight %}

{% highlight Python %}
%%time
into(DataFrame, by(t2.action_taken_name,
                   t2.action_taken_name.count()).sort('action_taken_name_count',
                                                      ascending=False))
{% endhighlight %}

    CPU times: user 4.13 ms, sys: 844 µs, total: 4.97 ms
    Wall time: 954 ms

Here the indexed MongoDB system seems about twice as fast as the comparably
indexed SQLite system.

Results
-------

*Disclaimer: These results come from a single run.  No attempt was made to
optimize the backend configuration, nor was any consideration taken into
account about databases being warmed up.  These numbers are far from
conclusive, and are merely here to present the ease with which
intuitive-building experiments are easy with Blaze and the value of choosing
the right backend.*

<table>
  <thead>
    <tr style="text-align: right;">
      <th>Backend</th>
      <th>Duration</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td> NumPy/Pandas </td>
      <td> <i>need bigger machine</i> </td>
    </tr>
    <tr>
      <td> Python/CSV </td>
      <td> 14 minutes </td>
    </tr>
    <tr>
      <td> SQLite </td>
      <td> 7 seconds </td>
    </tr>
    <tr>
      <td> MongoDB </td>
      <td> 7 seconds </td>
    </tr>
    <tr>
      <td> SQLite (indexed) </td>
      <td> 2 seconds</td>
    </tr>
    <tr>
      <td> MongoDB (indexed) </td>
      <td> 1 second </td>
    </tr>
  </tbody>
</table>

Conclusion
==========

Blaze enables you to investigate, transform, and migrate large data
intuitively. You can choose the right technology for your application
without having to worry about learning a new syntax.

We hope that by lowering this barrier more users will use the right tool for
the job.


More Information
----------------

*   Documentation: [blaze.pydata.org/](http://blaze.pydata.org/)
*   Source: [github.com/ContinuumIO/blaze/](http://github.com/ContinuumIO/blaze/)
*   Install with [Anaconda](https://store.continuum.io/cshop/anaconda/):

        conda install blaze
