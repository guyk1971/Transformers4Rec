import pytest

from tests.tf import _utils as test_utils
from transformers4rec.utils.tags import Tag

tf4rec = pytest.importorskip("transformers4rec.tf")


def test_tabular_features(yoochoose_schema, tf_yoochoose_like):
    tab_module = tf4rec.TabularFeatures.from_schema(yoochoose_schema)

    outputs = tab_module(tf_yoochoose_like)

    assert (
        list(outputs.keys())
        == yoochoose_schema.select_by_tag(Tag.CONTINUOUS).column_names
        + yoochoose_schema.select_by_tag(Tag.CATEGORICAL).column_names
    )


def test_serialization_tabular_features(yoochoose_schema, tf_yoochoose_like):
    inputs = tf4rec.TabularFeatures.from_schema(yoochoose_schema)

    copy_layer = test_utils.assert_serialization(inputs)

    assert list(inputs.to_merge.keys()) == list(copy_layer.to_merge.keys())


def test_tabular_features_with_projection(yoochoose_schema, tf_yoochoose_like):
    tab_module = tf4rec.TabularFeatures.from_schema(yoochoose_schema, continuous_projection=64)

    outputs = tab_module(tf_yoochoose_like)

    assert len(outputs.keys()) == 3
    assert all(len(tensor.shape) == 2 for tensor in outputs.values())
    assert all(tensor.shape[-1] == 64 for tensor in outputs.values())


@test_utils.mark_run_eagerly_modes
@pytest.mark.parametrize("continuous_projection", [None, 128])
def test_tabular_features_yoochoose_model(
    yoochoose_schema, tf_yoochoose_like, run_eagerly, continuous_projection
):
    inputs = tf4rec.TabularFeatures.from_schema(
        yoochoose_schema, continuous_projection=continuous_projection, aggregation="concat"
    )

    body = tf4rec.SequentialBlock([inputs, tf4rec.MLPBlock([64])])

    test_utils.assert_body_works_in_model(tf_yoochoose_like, inputs, body, run_eagerly)