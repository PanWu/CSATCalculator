'''
    File name: csat_calculator.py
    Author: Pan Wu (https://www.linkedin.com/in/panwu/)
    Date created: 4/27/2021
    Date last modified: 4/27/2021
    Python Version: 3.7
'''

import streamlit as st
import numpy as np
import pandas as pd
from scipy import stats

st.title('CSAT Calculator')
st.write('''Simplify your CSAT calculation with a statistical rigor.
    Please input survey response result on the left-sidebar''')

#############################################################################
st.header('Part 1. CSAT calculation (without confidence interval)')
# generate the side bar for survey result input, survey have 5 rating levels
# default values are set with survey result {1, 5, 3, 4, 5, 2, 1, 4, 3, 4}
default_response = [2, 1, 2, 3, 2]
n_level = 5
res_list = [
    st.sidebar.number_input(
        '# response with {0} star(s): '.format(i+1),
        min_value=0, max_value=None, step=1, value=default_response[i],
        key='res_list_{0}'.format(i), format='%d')
    for i in range(n_level)
]
survey_result = np.array(res_list)
df_survey = pd.DataFrame({'rating': range(1, 6), 'count': survey_result})
st.write(df_survey)

# calculate CSAT score and percentage without confidence interval calculation
csat_score = (df_survey['rating'] * df_survey['count']).sum() \
    / df_survey['count'].sum()
csat_percent = df_survey.query('rating >= 4')['count'].sum() \
    / df_survey['count'].sum()
st.write('... # of survey with response:  {:d}'.format(
    df_survey['count'].sum()))
st.write('... CSAT score is:         {:.2f}'.format(csat_score))
st.write('... CSAT percentage is:    {:.2f}'.format(csat_percent))

#############################################################################
st.header('Part 2. CSAT (with confidence interval)')
# generate the side bar for conf interval, default at 0.95
conf_level = st.sidebar.slider(
    'Please choose the confidence level:',
    0.80, 0.99, value=0.95, step=0.01)
survey_count = df_survey['count'].sum()
degrees_freedom = survey_count - 1
st.write('(degree of freedom, confidence level): ({0:d}, {1:.2f})'.format(
    degrees_freedom, conf_level))

df_survey_1 = df_survey.assign(diff=lambda x: x['rating'] - csat_score) \
        .assign(diff2=lambda x: x['diff'] ** 2 * x['count'])
std_sample = np.sqrt(df_survey_1['diff2'].sum() / degrees_freedom)
# calculate std for CSAT score
std_csat_score = std_sample / np.sqrt(survey_count)

# calculate std for CSAT percent
std_csat_percent = np.sqrt(csat_percent * (1-csat_percent) / survey_count)

# calculate confidence interval based on t test
csat_score_low, csat_score_high = stats.t.interval(
    conf_level, degrees_freedom, csat_score, std_csat_score)
csat_percent_low, csat_percent_high = stats.t.interval(
    conf_level, degrees_freedom, csat_percent, std_csat_percent)
st.write('... CSAT score is:      {0:.2f} ({1:.2f}, {2:.2f})'.format(
    csat_score, csat_score_low, csat_score_high))
st.write('... CSAT percentage is: {0:.2f} ({1:.2f}, {2:.2f})'.format(
    csat_percent, csat_percent_low, csat_percent_high))

#############################################################################
st.header('Part 3. CSAT (with conf interval + finite population correction)')
survey_total = st.number_input(
    '# Total survey sent out (regardless with response or not): ',
    value=survey_count, min_value=0, max_value=None, step=1,
    key='survey_total', format='%d')
# add finite population correction (use default zero to avoid nan)
fpc = np.sqrt((survey_total - survey_count) / (survey_total - 1))
default_zero = 0.00000001

# calculate confidence interval based on t test
csat_score_low_fpc, csat_score_high_fpc = stats.t.interval(
    conf_level, degrees_freedom, csat_score,
    std_csat_score * max(fpc, default_zero))
csat_percent_low_fpc, csat_percent_high_fpc = stats.t.interval(
    conf_level, degrees_freedom, csat_percent,
    std_csat_percent * max(fpc, default_zero))
st.write('... CSAT score is:      {0:.2f} ({1:.2f}, {2:.2f})'.format(
    csat_score, csat_score_low_fpc, csat_score_high_fpc))
st.write('... CSAT percentage is: {0:.2f} ({1:.2f}, {2:.2f})'.format(
    csat_percent, csat_percent_low_fpc, csat_percent_high_fpc))

st.write(' ------------- ')
st.write('''Have a question? Reach out to Pan (author) at
    https://www.linkedin.com/in/panwu/''')
