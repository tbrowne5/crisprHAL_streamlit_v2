# TevSaCas9 Model — Compatibility Notes

**Status:** Disabled in the Streamlit app pending resolution.
**Model file:** `models/TEVSACAS9.h5`
**Root cause:** Keras 2 → Keras 3 breaking changes in GRU layer serialization.

---

## Background

The `TEVSACAS9.h5` file was saved using an older version of TensorFlow/Keras (Keras 2).
The three SpCas9 models (`TEVSPCAS9.keras`, `ESPCAS9.keras`, `WT-SPCAS9.keras`) use the
newer `.keras` format introduced with Keras 3 (TF 2.16+) and load without issue.

Keras 3, shipped with TensorFlow 2.16 and later, introduced breaking changes to the GRU
layer's serialized configuration format. Specifically, two parameters present in all Keras 2
GRU configs were removed:

| Parameter | Keras 2 value | Keras 3 status |
|-----------|--------------|----------------|
| `time_major` | `False` | Removed |
| `implementation` | `1` | Removed |

---

## Errors Encountered

### Error 1 — Class not found
```
Could not locate class 'GRU'. Make sure custom classes are decorated with
@keras.saving.register_keras_serializable().
```
**Cause:** Keras 3's H5 loader cannot resolve the string `'GRU'` from the model config to
a class, because Keras 3's GRU is registered under a different internal path than Keras 2's.

**Attempted fix:** Pass `custom_objects={"GRU": tf.keras.layers.GRU}` to
`tf.keras.models.load_model`. This resolved the class lookup for the first deserialization
pass but exposed a second error.

---

### Error 2 — Unrecognized keyword arguments
```
Unrecognized keyword arguments passed to GRU: {'time_major': False}
```
**Cause:** Even with the class found, Keras 3's GRU `__init__` no longer accepts
`time_major` or `implementation`, which are still present in the H5 model config.

**Attempted fix:** Subclass `tf.keras.layers.GRU` as `_LegacyGRU`, absorbing the
legacy kwargs in `__init__`:
```python
class _LegacyGRU(tf.keras.layers.GRU):
    def __init__(self, *args, time_major=False, implementation=1, **kwargs):
        super().__init__(*args, **kwargs)
```
Pass `custom_objects={"GRU": _LegacyGRU}`. This resolved instantiation but exposed a
third error.

---

### Error 3 — Custom class not in Keras registry (multi-pass deserialization)
```
Could not locate class '_LegacyGRU'. Full object config:
{'class_name': '_LegacyGRU', 'registered_name': '_LegacyGRU', ...}
```
**Cause:** Keras 3's H5 loading is multi-pass. After the first pass maps `'GRU'` →
`_LegacyGRU` and instantiates the layer, Keras 3 re-serializes the `Bidirectional`
wrapper's inner layer — now recording it as `_LegacyGRU` — and immediately attempts
to deserialize it again. Since `_LegacyGRU` is not in Keras's global class registry,
the second lookup fails.

**Attempted fix:** Add `@tf.keras.saving.register_keras_serializable(package="Custom")`
to `_LegacyGRU`, which registers the class in the Keras registry so both passes resolve.

---

### Error 4 — Invalid attribute path in TF 2.21
```
AttributeError: ...
File "streamlit_app.py", line 162, in <module>
    @tf.keras.saving.register_keras_serializable(package="Custom")
AttributeError: module 'tensorflow.python.util.lazy_loader' has no attribute 'saving'
```
**Cause:** `tf.keras.saving` is not a valid attribute path in TensorFlow 2.21. The
`register_keras_serializable` function is accessible via `keras.saving` (standalone Keras 3
package) or `tf.keras.utils`, but not through `tf.keras.saving`. The decorator crashed the
app at import time before any model loading occurred.

**Attempted fix:** Replace the entire class-based approach with direct H5 config patching
via `h5py`: read the model config JSON from the H5 file, recursively strip `time_major` and
`implementation` from every GRU block, reconstruct the model with `model_from_json`, then
load weights. This avoided all class and registry issues, but the error persisted — the
`model.load_weights` step appears to encounter additional incompatibilities between the
Keras 2 weight storage format and Keras 3's loader.

---

## Current Status

The model has been disabled in the Streamlit app. The other three models (TevSpCas9,
eSpCas9, WT-SpCas9) are unaffected.

---

## Recommended Resolution

The most reliable path forward is to **re-save `TEVSACAS9.h5` in the `.keras` format**
using a Keras 2 / TF 2.15 environment, then update the model registry entry to point to
the new file. This is the same format used by all three SpCas9 models and loads without
any compatibility shims.

```bash
# In a TF 2.15 environment:
import tensorflow as tf
model = tf.keras.models.load_model("models/TEVSACAS9.h5")
model.save("models/TEVSACAS9.keras")
```

Alternatively, re-exporting the model from the crisprHAL training pipeline with TF 2.16+
would produce a natively compatible `.keras` file.

Once the file is re-saved, update `MODELS["TevSaCas9"]["path"]` in `streamlit_app.py`
from `"models/TEVSACAS9.h5"` to `"models/TEVSACAS9.keras"` and remove this note.
