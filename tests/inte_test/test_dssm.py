import os
import pytest
import shutil
import numpy as np

from matchzoo import datapack
from matchzoo import generators
from matchzoo import preprocessor
from matchzoo import models
from matchzoo import engine


def prepare_data():
    """Prepare train & test data."""
    train = []
    test = []
    path = os.path.dirname(__file__)
    with open(os.path.join(path, 'train.txt')) as f:
        train = [tuple(map(str, i.split('\t'))) for i in f]
    with open(os.path.join(path, 'test.txt')) as f:
        test = [tuple(map(str, i.split('\t'))) for i in f]
    return train, test


def inte_test_dssm():
    """Test DSSM model."""
    # load data.
    train, test = prepare_data()
    # do pre-processing.
    dssm_preprocessor = preprocessor.DSSMPreprocessor()
    processed_train = dssm_preprocessor.fit_transform(train, stage='train')
    # the dimension of dssm model is the length of tri-letters.
    dim_triletter = processed_train.context['dim_triletter']
    # generator.
    generator = generators.PointGenerator(processed_train)
    X, y = generator[0]
    # Create a dssm model
    dssm_model = models.DSSMModel()
    dssm_model.params['input_shapes'] = [(dim_triletter, ), (dim_triletter, )]
    dssm_model.guess_and_fill_missing_params()
    dssm_model.build()
    dssm_model.compile()
    dssm_model.fit([X.text_left, X.text_right], y)
    dssm_model.save('.tmpdir')

    # testing
    processed_test = dssm_preprocessor.fit_transform(test, stage='test')
    generator = generators.PointGenerator(processed_test)
    X, y = generator[0]
    dssm_model = engine.load_model('.tmpdir')
    predictions = dssm_model.predict([X.text_left, X.text_right])
    assert len(predictions) > 0
    assert type(predictions[0][0]) == np.float32
    shutil.rmtree('.tmpdir')

    
if __name__ == '__main__':
    inte_test_dssm()
