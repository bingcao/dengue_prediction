import logging

import fhub_core.contrib
import numpy as np
import sklearn.decomposition
import sklearn.preprocessing
from fhub_core.feature import Feature
from fhub_core.util.modutil import import_module_from_modname
from fhub_transformers import IdentityTransformer, SimpleFunctionTransformer
from fhub_transformers.missing import LagImputer, NullFiller, NullIndicator
from fhub_transformers.ts import SingleLagger

from dengue_prediction.config import cg

logger = logging.getLogger(__name__)


def get_contrib_features():
    modname = cg('contrib', 'module_name')
    mod = import_module_from_modname(modname)
    return fhub_core.contrib.get_contrib_features(mod)


def get_feature_transformations():
    features = []

    features.append(
        Feature(
            input='ndvi_se',
            transformer=[
                LagImputer(groupby_kwargs={'level': 'city'}),
                sklearn.preprocessing.Imputer(),
                sklearn.preprocessing.StandardScaler(),
            ]
        )
    )

    features.append(
        Feature(
            input='ndvi_sw',
            transformer=[
                LagImputer(groupby_kwargs={'level': 'city'}),
                sklearn.preprocessing.Imputer(),
                sklearn.preprocessing.StandardScaler(),
            ]
        )
    )

    features.append(
        Feature(
            input='precipitation_amt_mm',
            transformer=[
                LagImputer(groupby_kwargs={'level': 'city'}),
                sklearn.preprocessing.Imputer(),
                SimpleFunctionTransformer(np.log1p)
            ]
        )
    )

    features.append(
        Feature(
            input='precipitation_amt_mm',
            transformer=[
                NullIndicator(),
            ]
        )
    )

    # Same basic cleaning of time series features.
    for input_ in [
        'reanalysis_air_temp_k',
        'reanalysis_avg_temp_k',
        'reanalysis_dew_point_temp_k',
        'reanalysis_max_air_temp_k',
        'reanalysis_min_air_temp_k',
        'reanalysis_precip_amt_kg_per_m2',
        'reanalysis_relative_humidity_percent',
        'reanalysis_specific_humidity_g_per_kg',
        'reanalysis_tdtr_k',

        'station_avg_temp_c',
        'station_diur_temp_rng_c',
        'station_max_temp_c',
        'station_min_temp_c',
        'station_precip_mm',
    ]:
        features.append(
            Feature(
                input=input_,
                transformer=[
                    LagImputer(groupby_kwargs={'level': 'city'}),
                    NullFiller(replacement=0.0),
                    sklearn.preprocessing.StandardScaler(),
                ]
            )
        )

    features.append(
        Feature(
            input='reanalysis_sat_precip_amt_mm',
            transformer=[
                SingleLagger(1, groupby_kwargs={'level': 'city'}),
                LagImputer(groupby_kwargs={'level': 'city'}),
                NullFiller(replacement=0.0),
            ]
        )
    )

    features.append(
        Feature(
            input=['reanalysis_sat_precip_amt_mm',
                   'reanalysis_relative_humidity_percent',
                   'reanalysis_specific_humidity_g_per_kg',
                   'reanalysis_precip_amt_kg_per_m2',
                   'precipitation_amt_mm',
                   'station_precip_mm',
                   ],
            transformer=[
                LagImputer(groupby_kwargs={'level': 'city'}),
                sklearn.preprocessing.Imputer(),
                sklearn.decomposition.PCA(n_components=2),
            ]
        )
    )

    # add contributed features
    contrib_features = get_contrib_features()
    features.extend(contrib_features)

    return features


def get_target_transformations():
    transformations = []
    transformations.append(
        Feature(
            input='total_cases',
            transformer=IdentityTransformer(),
        )
    )
    return transformations
