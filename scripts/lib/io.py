"""
I/O utilities for AlphaFold MCP scripts.

These functions handle file reading/writing and FASTA operations.
Extracted and simplified from use case scripts.
"""

from pathlib import Path
from typing import Union, Dict, List, Tuple
import os


def load_fasta(file_path: Union[str, Path]) -> Dict[str, str]:
    """
    Load FASTA file and return dict of {header: sequence}.

    Args:
        file_path: Path to FASTA file

    Returns:
        Dictionary mapping sequence headers to sequences

    Example:
        >>> sequences = load_fasta("protein.fasta")
        >>> print(sequences.keys())
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"FASTA file not found: {file_path}")

    sequences = {}
    current_header = None
    current_sequence = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                # Save previous sequence
                if current_header:
                    sequences[current_header] = ''.join(current_sequence)
                # Start new sequence
                current_header = line[1:]  # Remove '>'
                current_sequence = []
            elif line:
                current_sequence.append(line)

    # Save last sequence
    if current_header:
        sequences[current_header] = ''.join(current_sequence)

    return sequences


def save_fasta(sequences: Dict[str, str], file_path: Union[str, Path]) -> None:
    """
    Save sequences to FASTA file.

    Args:
        sequences: Dictionary mapping headers to sequences
        file_path: Output file path
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        for header, sequence in sequences.items():
            # Ensure header starts with '>'
            if not header.startswith('>'):
                header = f'>{header}'
            f.write(f"{header}\n")

            # Write sequence in 80-character lines
            for i in range(0, len(sequence), 80):
                f.write(f"{sequence[i:i+80]}\n")


def analyze_fasta_content(file_path: Union[str, Path]) -> Dict[str, any]:
    """
    Analyze FASTA file content to determine if it's monomer or multimer.

    Args:
        file_path: Path to FASTA file

    Returns:
        Dictionary containing:
        - num_sequences: Number of sequences
        - total_length: Total amino acid count
        - sequences: List of (header, length) tuples
        - is_multimer: True if multiple sequences
        - complex_type: 'monomer', 'homodimer', 'heterodimer', 'multimer'
    """
    sequences = load_fasta(file_path)

    sequence_info = [(header, len(seq)) for header, seq in sequences.items()]
    num_sequences = len(sequences)
    total_length = sum(length for _, length in sequence_info)

    # Determine complex type
    if num_sequences == 1:
        complex_type = 'monomer'
    elif num_sequences == 2:
        seq_values = list(sequences.values())
        if seq_values[0] == seq_values[1]:
            complex_type = 'homodimer'
        else:
            complex_type = 'heterodimer'
    else:
        # Check if all sequences are the same (homo-oligomer)
        seq_values = list(sequences.values())
        if all(seq == seq_values[0] for seq in seq_values):
            complex_type = f'homo-{num_sequences}mer'
        else:
            complex_type = 'multimer'

    return {
        'num_sequences': num_sequences,
        'total_length': total_length,
        'sequences': sequence_info,
        'is_multimer': num_sequences > 1,
        'complex_type': complex_type
    }


def ensure_directory(dir_path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        dir_path: Directory path

    Returns:
        Path object for the directory
    """
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def safe_filename(name: str) -> str:
    """
    Convert string to safe filename by removing/replacing invalid characters.

    Args:
        name: Original name

    Returns:
        Safe filename
    """
    # Replace problematic characters
    safe_chars = []
    for c in name:
        if c.isalnum() or c in '-_':
            safe_chars.append(c)
        elif c in ' .':
            safe_chars.append('_')

    result = ''.join(safe_chars).strip('_')
    return result if result else 'protein'