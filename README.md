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
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploying on Streamlit Community Cloud

1. Fork this repository
2. Connect it at [share.streamlit.io](https://share.streamlit.io)
3. Set the main file to `streamlit_app.py`

`runtime.txt` pins Python 3.11 and `requirements.txt` uses `tensorflow-cpu==2.19.0` (CPU-only, appropriate for Streamlit Community Cloud's CPU-only environment).

## Data availability

Raw sequence reads from which the training datasets are derived are available at:
* https://www.ncbi.nlm.nih.gov/bioproject/PRJNA939699
* https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1260991
* https://www.ncbi.nlm.nih.gov/bioproject/PRJNA450978

## Citations

Browne, T.S. et al. Better data for better predictions: data curation improves deep learning for sgRNA/Cas9 prediction. **bioRxiv** (Pre-Print, 2025). https://doi.org/10.1101/2025.06.24.661356

Ham, D.T., Browne, T.S. et al. PAM adenine methylation and flanking sequence regulate SaCas9 activity in bacteria. **Nucleic Acids Res** (2025). https://doi.org/10.1093/nar/gkaf1520

Ham, D.T., Browne, T.S., Banglorewala, P.N. et al. A generalizable Cas9/sgRNA prediction model using machine transfer learning with small high-quality datasets. **Nat Commun** *14*, 5514 (2023). https://doi.org/10.1038/s41467-023-41143-7

Guo, J. et al. Improved sgRNA design in bacteria via genome-wide activity profiling. **Nucleic Acids Res** *46*, 7052–7069 (2018).

Abadi, M. et al. TensorFlow: Large-scale machine learning on heterogeneous systems (2015). https://tensorflow.org

Virtanen, P. et al. SciPy 1.0: fundamental algorithms for scientific computing in python. **Nat Methods** *17*, 261–272 (2020).
