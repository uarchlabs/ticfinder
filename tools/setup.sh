export PACINO="$(realpath ../pacino)"
export WRITING_SAMPLES="$(realpath ../../writing_samples)"
if python3 -c 'import spacy' 2>/dev/null; then
  export SPACY_INSTALLED="yes"
else
  export SPACY_INSTALLED="no"
fi
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000
