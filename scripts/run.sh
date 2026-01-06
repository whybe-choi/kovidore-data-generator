#!/bin/bash

# Default values
SUBSETS="cybersecurity"
TASK="single_section_summary"
MODEL_ALIAS="upstage-solar-pro2"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --subsets)
            shift
            SUBSETS=""
            while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                SUBSETS="$SUBSETS $1"
                shift
            done
            SUBSETS="${SUBSETS:1}"  # Remove leading space
            ;;
        --task)
            TASK="$2"
            shift 2
            ;;
        --model_alias)
            MODEL_ALIAS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
echo "Running with:"
echo "  SUBSETS: $SUBSETS"
echo "  TASK: $TASK"
echo "  MODEL_ALIAS: $MODEL_ALIAS"
echo ""

kovidore-data-generator preprocess \
    --subsets $SUBSETS \
    --task $TASK

kovidore-data-generator pipeline \
    --model_alias $MODEL_ALIAS \
    --subsets $SUBSETS \
    --task $TASK