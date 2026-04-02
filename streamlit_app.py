import io
import numpy as np
import pandas as pd
import streamlit as st
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns

from processing import processing

# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

MODELS = {
    "TevSpCas9": {
        "path": "models/TEVSPCAS9.keras",
        "params": [37, 3, 14, 0],
        "pam": "NGG",
        "organism": "E. coli / C. rodentium",
        "min_input_nt": 37,
        "in_progress": False,
        "description": (
            "Recommended for TevSpCas9 and SpCas9 activity prediction. "
            "Lowest compute requirements."
        ),
        "input_note": (
            "37 nt context: 3 upstream + 20 sgRNA + 14 downstream (NGG PAM + 11)"
        ),
        "citations": [
            (
                "crisprHAL v2",
                "Browne, T.S. et al. Better data for better predictions: data "
                "curation improves deep learning for sgRNA/Cas9 prediction. "
                "*bioRxiv* (2025).",
                "https://doi.org/10.1101/2025.06.24.661356",
            ),
            (
                "crisprHAL",
                "Ham, D.T., Browne, T.S., Banglorewala, P.N. et al. A generalizable "
                "Cas9/sgRNA prediction model using machine transfer learning with small "
                "high-quality datasets. *Nat Commun* **14**, 5514 (2023).",
                "https://doi.org/10.1038/s41467-023-41143-7",
            ),
        ],
        "data": [
            ("PRJNA939699", "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA939699"),
            ("PRJNA1260991", "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1260991"),
        ],
    },
    "eSpCas9": {
        "path": "models/ESPCAS9.keras",
        "params": [406, 193, 193, 0],
        "pam": "NGG",
        "organism": "E. coli",
        "min_input_nt": 406,
        "in_progress": False,
        "description": (
            "Enhanced SpCas9 variant. "
            "Requires input sequences ≥ 406 nt."
        ),
        "input_note": (
            "406 nt context: 193 upstream + 20 sgRNA + 193 downstream (NGG PAM + 190)"
        ),
        "citations": [
            (
                "crisprHAL v2",
                "Browne, T.S. et al. Better data for better predictions: data "
                "curation improves deep learning for sgRNA/Cas9 prediction. "
                "*bioRxiv* (2025).",
                "https://doi.org/10.1101/2025.06.24.661356",
            ),
            (
                "Training data",
                "Guo, J. et al. Improved sgRNA design in bacteria via genome-wide "
                "activity profiling. *Nucleic Acids Res* **46**, 7052–7069 (2018).",
                "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA450978",
            ),
        ],
        "data": [
            ("PRJNA450978", "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA450978"),
        ],
    },
    "WT-SpCas9": {
        "path": "models/WT-SPCAS9.keras",
        "params": [378, 189, 169, 0],
        "pam": "NGG",
        "organism": "E. coli",
        "min_input_nt": 378,
        "in_progress": False,
        "description": (
            "Wild-type SpCas9. Secondary SpCas9 prediction model. "
            "Requires input sequences ≥ 378 nt."
        ),
        "input_note": (
            "378 nt context: 189 upstream + 20 sgRNA + 169 downstream (NGG PAM + 166)"
        ),
        "citations": [
            (
                "crisprHAL v2",
                "Browne, T.S. et al. Better data for better predictions: data "
                "curation improves deep learning for sgRNA/Cas9 prediction. "
                "*bioRxiv* (2025).",
                "https://doi.org/10.1101/2025.06.24.661356",
            ),
            (
                "crisprHAL",
                "Ham, D.T., Browne, T.S., Banglorewala, P.N. et al. A generalizable "
                "Cas9/sgRNA prediction model using machine transfer learning with small "
                "high-quality datasets. *Nat Commun* **14**, 5514 (2023).",
                "https://doi.org/10.1038/s41467-023-41143-7",
            ),
        ],
        "data": [
            ("PRJNA939699", "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA939699"),
            ("PRJNA1260991", "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1260991"),
        ],
    },
    "TevSaCas9": {
        "path": "models/TEVSACAS9.h5",
        "params": [29, 1, 8, 1],
        "pam": "NNGRRN",
        "organism": "S. aureus",
        "min_input_nt": 29,
        "in_progress": True,
        "description": (
            "SaCas9 and TevSaCas9 activity prediction. Uses NNGRRN PAM. "
            "Note: this model is still in active development."
        ),
        "input_note": (
            "29 nt context: 1 upstream + 20 sgRNA + 8 downstream (NNGRRN PAM + 2)"
        ),
        "citations": [
            (
                "crisprHAL SaCas9",
                "Ham, D.T., Browne, T.S. et al. PAM adenine methylation and flanking "
                "sequence regulate SaCas9 activity in bacteria. "
                "*Nucleic Acids Res* (2025).",
                "https://doi.org/10.1093/nar/gkaf1520",
            ),
            (
                "crisprHAL",
                "Ham, D.T., Browne, T.S., Banglorewala, P.N. et al. A generalizable "
                "Cas9/sgRNA prediction model using machine transfer learning with small "
                "high-quality datasets. *Nat Commun* **14**, 5514 (2023).",
                "https://doi.org/10.1038/s41467-023-41143-7",
            ),
        ],
        "data": [
            ("PRJNA450978", "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA450978"),
        ],
    },
}

proc = processing()


# ---------------------------------------------------------------------------
# Cached model loader — prevents reloading on every Streamlit rerun
# ---------------------------------------------------------------------------

@st.cache_resource
def load_model(path: str):
    # .h5 models were saved with Keras 2; Keras 3 (TF 2.16+) cannot locate the
    # 'GRU' class by name during H5 deserialization. Supplying it explicitly via
    # custom_objects resolves the mismatch without altering model behaviour.
    if path.endswith(".h5"):
        return tf.keras.models.load_model(
            path,
            custom_objects={"GRU": tf.keras.layers.GRU},
        )
    return tf.keras.models.load_model(path)


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="crisprHAL",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    "<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("crisprHAL")
    st.caption("v2.0.0 — Updated models")

    st.divider()

    model_name = st.selectbox(
        "Nuclease model",
        list(MODELS.keys()),
        index=0,
        help="Select the Cas9 variant that matches your experimental system.",
    )
    meta = MODELS[model_name]

    if meta["in_progress"]:
        st.warning("This model is still in active development.", icon="⚠️")

    st.markdown(f"**PAM:** `{meta['pam']}`")
    st.markdown(f"**Organism:** *{meta['organism']}*")
    st.markdown(f"**Min. sequence length:** {meta['min_input_nt']} nt")
    st.caption(meta["description"])

    with st.expander("Citations"):
        for label, text, url in meta["citations"]:
            st.markdown(f"**{label}:** {text} [→]({url})")
        st.markdown("**Training data:**")
        for acc, url in meta["data"]:
            st.markdown(f"[{acc}]({url})")

    st.divider()

    st.subheader("Options")
    circular = st.checkbox(
        "Circular DNA",
        value=False,
        help="Wrap sequence ends to find targets spanning the origin (plasmids, circular chromosomes).",
    )
    rev_comp = st.checkbox(
        "Include reverse complement",
        value=True,
        help="Search both strands of the input sequence.",
    )
    top_n = st.slider("Top results to display", min_value=1, max_value=100, value=10)

    st.divider()

    st.markdown("**Resources**")
    st.markdown("[tbrowne5/crisprHAL](https://github.com/tbrowne5/crisprHAL) — model repository")
    st.markdown("[tbrowne5/crisprHAL_streamlit_v2](https://github.com/tbrowne5/crisprHAL_streamlit_v2) — this app")

    st.divider()

    st.caption("Looking for the V1 models?")
    st.markdown("[crisprHAL V1 →](https://crisprhal.streamlit.app)")


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("crisprHAL")
st.subheader("A generalizable bacterial Cas9/sgRNA activity prediction model")

uploaded_file = st.file_uploader(
    "Upload a sequence file",
    type=["fasta", "fa", "txt", "csv", "tsv"],
    help=(
        "FASTA for genomic sequences — PAM sites are detected automatically. "
        "CSV/TSV for pre-extracted full-context sequences."
    ),
)

with st.expander("Input format guide"):
    left_ctx = meta["params"][1]
    right_ctx = meta["params"][2]
    total_len = meta["params"][0]
    st.markdown(
        f"""
**FASTA** *(recommended — PAM sites detected automatically)*
```
>sequence_name
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC...
```
Each sequence must be ≥ **{total_len} nt** for the selected model ({model_name}).
Both strands are scanned by default.

**CSV / TSV** *(pre-extracted full-context sequences)*

Sequences must be exactly **{total_len} nt** ({meta['input_note']}).
```
{"-" * total_len}
```
One sequence per line. An optional second column with experimental scores is ignored.
        """
    )


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

if uploaded_file is not None:
    if st.button("Run Prediction", type="primary"):
        filename = uploaded_file.name
        content = uploaded_file.getvalue().decode("utf-8")

        try:
            # --- Parse input ---
            if filename.endswith((".fasta", ".fa", ".txt")):
                with st.spinner("Scanning for target sites…"):
                    sequences, encoded, _ = proc.process_fasta(
                        io.StringIO(content),
                        meta["params"],
                        circular,
                        rev_comp,
                    )
            elif filename.endswith((".csv", ".tsv")):
                with st.spinner("Reading sequences…"):
                    sequences, encoded, _ = proc.process_csv(
                        io.StringIO(content), filename
                    )
            else:
                st.error("Unsupported file type. Please upload FASTA, CSV, or TSV.")
                st.stop()

            if len(sequences) == 0:
                st.warning(
                    f"No valid sgRNA target sites found. "
                    f"Ensure sequences are ≥ {meta['min_input_nt']} nt and contain "
                    f"a valid `{meta['pam']}` PAM site."
                )
                st.stop()

            if len(sequences) > 50_000:
                st.warning(
                    f"Found {len(sequences):,} targets — prediction may be slow on CPU. "
                    "Consider splitting your input into smaller files."
                )

            # --- Predict ---
            with st.spinner(
                f"Running {model_name} on {len(sequences):,} target sequences…"
            ):
                model = load_model(meta["path"])
                predictions = model.predict(
                    encoded, batch_size=2048, verbose=0
                ).flatten()

            # --- Build results dataframe ---
            left_ctx = meta["params"][1]
            spacers = [s[left_ctx : left_ctx + 20] for s in sequences]
            df = (
                pd.DataFrame(
                    {
                        "sgRNA (20 nt)": spacers,
                        "Full context": sequences,
                        "Predicted activity": predictions,
                    }
                )
                .sort_values("Predicted activity", ascending=False)
                .reset_index(drop=True)
            )
            df.index += 1  # 1-based rank

            # --- Summary metrics ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Targets found", f"{len(df):,}")
            m2.metric("Best score", f"{df['Predicted activity'].max():.4f}")
            m3.metric("Mean score", f"{df['Predicted activity'].mean():.4f}")

            st.divider()

            plot_col, table_col = st.columns([3, 2])

            # --- Activity distribution plot ---
            with plot_col:
                fig, ax = plt.subplots(figsize=(8, 4))

                zones = [
                    (-3.5, -2.5, "#D9DD17"),
                    (-2.5, -1.5, "#A0D52F"),
                    (-1.5, -0.5, "#70C94B"),
                    (-0.5,  0.5, "#4ABB5F"),
                    ( 0.5,  1.5, "#2DA86F"),
                    ( 1.5,  2.5, "#1D9677"),
                    ( 2.5,  3.5, "#1B847D"),
                ]
                labels = [
                    "Rare", "Very Low", "Low", "Moderate", "High", "Very High", "Rare"
                ]
                for (x0, x1, color), label in zip(zones, labels):
                    ax.axvspan(x0, x1, color=color, alpha=1.0)
                    ax.annotate(
                        label,
                        xy=((x0 + x1) / 2, 0.93),
                        xycoords=("data", "axes fraction"),
                        ha="center",
                        fontsize=7,
                        color="black",
                    )

                use_kde = len(predictions) > 1
                sns.histplot(predictions, kde=use_kde, color="black", ax=ax)

                best = float(predictions.max())
                ax.axvline(x=best, color="red", linestyle="--", linewidth=2)
                ax.annotate(
                    "Best",
                    xy=(best + 0.15, 0.90),
                    xycoords=("data", "axes fraction"),
                    fontsize=10,
                    color="red",
                )

                ax.set_xlim(-3.5, 3.5)
                ax.set_title(
                    f"{model_name} — predicted activity distribution", color="white"
                )
                ax.set_xlabel("Predicted activity score", color="white")
                ax.set_ylabel("Count", color="white")
                for spine in ax.spines.values():
                    spine.set_color("white")
                ax.tick_params(colors="white")
                if ax.get_legend():
                    ax.get_legend().remove()
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)

                st.pyplot(fig)
                plt.close(fig)

            # --- Top-N guides table ---
            with table_col:
                display_n = min(top_n, len(df))
                st.subheader(f"Top {display_n} guides")
                top_df = df.head(display_n)[["sgRNA (20 nt)", "Predicted activity"]].copy()
                top_df["Predicted activity"] = top_df["Predicted activity"].map(
                    lambda x: f"{x:.4f}"
                )
                st.dataframe(top_df, use_container_width=True)

            # --- Download ---
            csv_bytes = df.to_csv(index=True, index_label="Rank").encode("utf-8")
            st.download_button(
                label="Download all results (CSV)",
                data=csv_bytes,
                file_name=f"crisprHAL_{model_name}_predictions.csv",
                mime="text/csv",
            )

        except Exception as exc:
            st.error(f"An error occurred during processing: {exc}")
