"""
processing.py — feature engineering for crisprHAL Streamlit v2

Adapted from tbrowne5/crisprHAL (processing.py) to accept file-like objects
(io.StringIO / Streamlit UploadedFile) instead of file paths.
"""

import numpy as np


class processing:

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # One-hot encoding
    # ------------------------------------------------------------------
    def onehotencode(self, nucleotideEncoding):
        """
        Map nucleotide sequences to one-hot arrays.
        A→[1,0,0,0]  C→[0,1,0,0]  G→[0,0,1,0]  T→[0,0,0,1]  N/M→[0,0,0,0]
        Returns ndarray of shape (N, seq_len, 4).
        """
        nt_map = {
            "A": [1, 0, 0, 0],
            "C": [0, 1, 0, 0],
            "G": [0, 0, 1, 0],
            "T": [0, 0, 0, 1],
            "M": [0, 0, 0, 0],
            "N": [0, 0, 0, 0],
        }
        encoded = []
        for seq in nucleotideEncoding:
            encoded.append(np.array([nt_map.get(nt.upper(), [0, 0, 0, 0]) for nt in seq]))
        return np.array(encoded)

    # ------------------------------------------------------------------
    # Target-site detection
    # ------------------------------------------------------------------
    def find_targets(self, sequence, inputParameters, circular=False, reverseComplement=True):
        """
        Scan a nucleotide sequence for CRISPR target sites with valid PAM.

        inputParameters: [total_len, left_ctx, right_ctx, pam_type]
          pam_type 0 → SpCas9 NGG
          pam_type 1 → SaCas9 NNGRRN (represented as GGG/GGA/GAG/GAA at offset)

        Returns a list of full-context strings of length total_len.
        """
        total_len, left_ctx, right_ctx, pam_type = inputParameters

        if len(sequence) < total_len:
            return []

        # PAM parameters
        if pam_type == 1:
            # SaCas9 NNGRRN: search for GGG/GGA/GAG/GAA at pamStart:pamEnd
            pam = ["GGG", "GGA", "GAG", "GAA"]
            pamStart, pamEnd = 2, 5
        else:
            # SpCas9 NGG: search for GG at offset +1/+2 from spacer end
            pam = ["GG"]
            pamStart, pamEnd = 1, 3

        sequence = (
            sequence.upper()
            .replace("U", "T")
            .replace(" ", "")
            .replace("\n", "")
        )

        if circular:
            sequence = sequence + sequence[: total_len - 1]

        targets = []

        def _scan(seq):
            for i in range(20 + left_ctx, len(seq) - right_ctx + 1):
                if seq[i + pamStart : i + pamEnd] in pam:
                    target = seq[i - (20 + left_ctx) : i + right_ctx]
                    if len(target) == total_len:
                        targets.append(target)
                    else:
                        break

        _scan(sequence)

        if reverseComplement:
            rc_seq = sequence[::-1].translate(str.maketrans("ACGT", "TGCA"))
            _scan(rc_seq)

        return targets

    # ------------------------------------------------------------------
    # FASTA input (file-like object)
    # ------------------------------------------------------------------
    def process_fasta(self, file_obj, inputParameters, circular=False, reverseComplement=True):
        """
        Parse a FASTA file-like object (io.StringIO or Streamlit UploadedFile).
        Calls find_targets() on each sequence record.
        Returns (sequences_list, one_hot_encoded, None).
        """
        inputSequences = []
        sequence = ""

        for line in file_obj:
            # Handle both str (StringIO) and bytes (BytesIO)
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            if line.startswith(">"):
                if sequence:
                    inputSequences += self.find_targets(
                        sequence, inputParameters, circular, reverseComplement
                    )
                    sequence = ""
            else:
                sequence += line.strip()

        # Last record
        if sequence:
            inputSequences += self.find_targets(
                sequence, inputParameters, circular, reverseComplement
            )

        if not inputSequences:
            return [], np.array([]), None

        return inputSequences, self.onehotencode(inputSequences), None

    # ------------------------------------------------------------------
    # CSV / TSV input (file-like object)
    # ------------------------------------------------------------------
    def process_csv(self, file_obj, filename="input.csv"):
        """
        Parse a CSV or TSV file-like object containing pre-defined sequences.
        Column 1: sgRNA / context sequence.
        Returns (sequences_list, one_hot_encoded, None).
        """
        delimiter = "\t" if filename.endswith(".tsv") else ","
        inputSequences = []

        for line in file_obj:
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(delimiter)
            seq = parts[0].strip()
            if seq:
                inputSequences.append(seq)

        if not inputSequences:
            return [], np.array([]), None

        return inputSequences, self.onehotencode(inputSequences), None
