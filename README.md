# crisprHAL Streamlit App — v2
The up-to-date web interface for [crisprHAL](https://github.com/tbrowne5/crisprHAL) bacterial Cas9/sgRNA on-target activity prediction.

## Links to the related repositories, papers, and web tools:
* [Up-to-date crisprHAL prediction tool repository](https://github.com/tbrowne5/crisprHAL)
* [crisprHAL V1 web app](https://crisprhal.streamlit.app) ([Repository](https://github.com/tbrowne5/crisprHAL_streamlit)) — V1 models (TevSpCas9, SpCas9, Citrobacter TevSpCas9)
* [crisprHAL 2.0 SpCas9 paper repository](https://github.com/tbrowne5/Better-data-for-better-predictions-data-curation-improves-deep-learning-for-sgRNA-Cas9-prediction/)
* [crisprHAL 2.0 SpCas9 pre-print](https://doi.org/10.1101/2025.06.24.661356)
* [crisprHAL SaCas9 paper repository](https://github.com/tbrowne5/Adenine-methylated-PAM-sequences-inhibit-SaCas9-activity)
* [crisprHAL SaCas9 publication](https://doi.org/10.1093/nar/gkaf1520)
* [crisprHAL SpCas9 publication](https://doi.org/10.1038/s41467-023-41143-7)

## Available Prediction Models:

| Model | PAM | Context required | Notes |
|-------|-----|-----------------|-------|
| TevSpCas9 | NGG | 37 nt | Recommended — fastest, lowest compute |
| eSpCas9 | NGG | 406 nt | Enhanced SpCas9 variant |
| WT-SpCas9 | NGG | 378 nt | Wild-type SpCas9, secondary model |
| TevSaCas9 | NNGRRN | 29 nt | *S. aureus* Cas9, in active development |

Context requirements match the crisprHAL command-line tool exactly:
* TevSpCas9: `37 nucleotides = 3 upstream, 20 sgRNA, 14 downstream (NGG PAM + 11)`
* eSpCas9: `406 nucleotides = 193 upstream, 20 sgRNA, 193 downstream (NGG PAM + 190)`
* WT-SpCas9: `378 nucleotides = 189 upstream, 20 sgRNA, 169 downstream (NGG PAM + 166)`
* TevSaCas9: `29 nucleotides = 1 upstream, 20 sgRNA, 8 downstream (NNGRRN PAM + 2)`

## Running locally

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploying on Streamlit Community Cloud

> **Python version must be set manually in the UI.**
> Streamlit Community Cloud currently ignores `runtime.txt`. The Python version
> must be selected in **Advanced Settings** before deploying — TensorFlow has no
> wheels for the current default (Python 3.14).

Steps:
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select the repo and set the main file to `streamlit_app.py`
4. Click **Advanced settings** → set **Python version to 3.13**
5. Deploy

If the app was already deployed with the wrong Python version, delete it and redeploy — the Python version cannot be changed on an existing deployment.

`requirements.txt` uses `tensorflow==2.21.0`, the earliest TF release with Python 3.13 wheel support. Models saved under TF 2.19 load correctly — TF maintains backward compatibility for `.keras` and `.h5` formats across minor versions.
